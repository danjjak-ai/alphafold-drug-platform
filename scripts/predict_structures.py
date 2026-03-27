"""
predict_structures.py — Phase 2: AlphaFold DB API 기반 단백질 구조 예측

AlphaFold EBI DB에서 사전 계산된 구조를 다운로드하여
data/structures/predicted/ 폴더에 저장하고
targets 테이블의 구조 출처 메타데이터를 업데이트한다.

사용법:
    python scripts/predict_structures.py
    python scripts/predict_structures.py --uniprot P02708 MUSK_UniProt LRP4_UniProt
    python scripts/predict_structures.py --force   # 이미 있어도 재다운로드
"""

import os
import sqlite3
import json
import sys
import argparse
import requests
import time

# ─────────────────────────────────────────────
# 기본 타겟 정의 (DB에 targets가 없을 때 폴백)
# ─────────────────────────────────────────────
DEFAULT_TARGETS = [
    {
        "uniprot_id": "P02708",
        "gene_name":  "CHRNA1",
        "name":       "Acetylcholine Receptor alpha-1",
    },
    {
        "uniprot_id": "O15146",
        "gene_name":  "MUSK",
        "name":       "Muscle Skeletal Receptor Tyrosine-Protein Kinase",
    },
    {
        "uniprot_id": "O94898",
        "gene_name":  "LRP4",
        "name":       "Low-density Lipoprotein Receptor-related Protein 4",
    },
]

ALPHAFOLD_API = "https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
REQUEST_TIMEOUT = 60  # seconds


# ─────────────────────────────────────────────
# DB 마이그레이션 — 컬럼 추가 (기존 데이터 보존)
# ─────────────────────────────────────────────
def migrate_db(conn: sqlite3.Connection):
    """targets 테이블에 구조 예측 관련 컬럼이 없으면 추가한다."""
    cur = conn.cursor()
    existing = {row[1] for row in cur.execute("PRAGMA table_info(targets)").fetchall()}

    migrations = [
        ("predicted_pdb_path",   "TEXT"),
        ("predicted_pdbqt_path", "TEXT"),
        ("predicted_plddt",      "REAL"),
        ("structure_source",     "TEXT DEFAULT 'rcsb_pdb'"),
        ("af_version",           "TEXT"),
        ("af_predicted_at",      "TEXT"),
    ]
    for col_name, col_def in migrations:
        if col_name not in existing:
            cur.execute(f"ALTER TABLE targets ADD COLUMN {col_name} {col_def}")
            print(f"  [DB] 컬럼 추가: targets.{col_name}")

    conn.commit()


# ─────────────────────────────────────────────
# AlphaFold DB API 호출
# ─────────────────────────────────────────────
def fetch_alphafold_metadata(uniprot_id: str) -> dict | None:
    """
    AlphaFold DB API에서 메타데이터(PDB URL, 버전 등)를 가져온다.
    반환값: {pdbUrl, paeImageUrl, modelCreatedDate, latestVersion, ...}
    """
    url = ALPHAFOLD_API.format(uniprot_id=uniprot_id)
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            if data and isinstance(data, list):
                return data[0]  # 가장 최신 버전
        elif resp.status_code == 404:
            print(f"  [AlphaFold DB] {uniprot_id}: 구조 없음 (404)")
        else:
            print(f"  [AlphaFold DB] {uniprot_id}: API 오류 {resp.status_code}")
    except requests.exceptions.Timeout:
        print(f"  [AlphaFold DB] {uniprot_id}: 타임아웃")
    except Exception as e:
        print(f"  [AlphaFold DB] {uniprot_id}: 오류 — {e}")
    return None


def download_pdb_from_url(pdb_url: str, output_path: str) -> bool:
    """PDB 파일을 URL에서 다운로드한다."""
    try:
        resp = requests.get(pdb_url, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(resp.text)
            return True
        print(f"  [다운로드 실패] HTTP {resp.status_code}: {pdb_url}")
    except Exception as e:
        print(f"  [다운로드 오류] {e}")
    return False


def parse_plddt_from_bfactor(pdb_path: str) -> float | None:
    """
    AlphaFold PDB 파일에서 B-factor 컬럼(= pLDDT 값)을 읽어
    평균 pLDDT를 계산한다.
    """
    plddt_values = []
    try:
        with open(pdb_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    try:
                        bfactor = float(line[60:66].strip())
                        plddt_values.append(bfactor)
                    except (ValueError, IndexError):
                        continue
    except Exception:
        return None

    if plddt_values:
        return round(sum(plddt_values) / len(plddt_values), 2)
    return None


def save_plddt_json(pdb_path: str, output_json: str):
    """잔기별 pLDDT 값을 JSON으로 저장한다."""
    per_residue = {}
    try:
        with open(pdb_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("ATOM"):
                    try:
                        res_seq  = int(line[22:26].strip())
                        res_name = line[17:20].strip()
                        bfactor  = float(line[60:66].strip())
                        key = f"{res_seq}:{res_name}"
                        if key not in per_residue:
                            per_residue[key] = bfactor
                    except (ValueError, IndexError):
                        continue
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(per_residue, f, indent=2)
    except Exception as e:
        print(f"  [pLDDT JSON 저장 오류] {e}")


# ─────────────────────────────────────────────
# 타겟별 예측 구조 처리
# ─────────────────────────────────────────────
def process_target(
    uniprot_id: str,
    gene_name: str,
    out_dir: str,
    force: bool = False,
) -> dict:
    """
    단일 타겟에 대해 AlphaFold DB 구조를 다운로드하고
    메타데이터 딕셔너리를 반환한다.

    반환값:
        {
          "success": bool,
          "pdb_path": str,
          "plddt_mean": float | None,
          "version": str | None,
          "predicted_at": str | None,
        }
    """
    gene_lower = gene_name.lower()
    pdb_path  = os.path.join(out_dir, f"{gene_lower}_alphafold.pdb")
    json_path = os.path.join(out_dir, f"{gene_lower}_plddt.json")

    # 이미 다운로드된 경우 스킵 (--force 아니면)
    if os.path.exists(pdb_path) and not force:
        print(f"  [{gene_name}] 기존 파일 사용: {pdb_path}")
        plddt = parse_plddt_from_bfactor(pdb_path)
        return {"success": True, "pdb_path": pdb_path,
                "plddt_mean": plddt, "version": None, "predicted_at": None}

    print(f"  [{gene_name}] AlphaFold DB 조회 중... (UniProt: {uniprot_id})")
    meta = fetch_alphafold_metadata(uniprot_id)
    if meta is None:
        return {"success": False, "pdb_path": None,
                "plddt_mean": None, "version": None, "predicted_at": None}

    pdb_url = meta.get("pdbUrl", "")
    version = str(meta.get("latestVersion", ""))
    predicted_at = meta.get("modelCreatedDate", "")

    print(f"  [{gene_name}] 구조 다운로드 중... (v{version}, {predicted_at})")
    ok = download_pdb_from_url(pdb_url, pdb_path)
    if not ok:
        return {"success": False, "pdb_path": None,
                "plddt_mean": None, "version": version, "predicted_at": predicted_at}

    # pLDDT 계산 및 JSON 저장
    plddt = parse_plddt_from_bfactor(pdb_path)
    save_plddt_json(pdb_path, json_path)

    print(f"  [{gene_name}] ✅ 완료 — 평균 pLDDT: {plddt:.1f}" if plddt else
          f"  [{gene_name}] ✅ 완료 (pLDDT 파싱 불가)")

    # pLDDT 경고
    if plddt is not None:
        if plddt >= 90:
            print(f"  [{gene_name}] 신뢰도: 매우 높음 (≥90) — 실험 구조 수준")
        elif plddt >= 70:
            print(f"  [{gene_name}] 신뢰도: 높음 (70~90) — 도킹 사용 가능")
        elif plddt >= 50:
            print(f"  [{gene_name}] 신뢰도: 보통 (50~70) — 결합 포켓 검토 권장")
        else:
            print(f"  [{gene_name}] ⚠ 신뢰도 낮음 (<50) — RCSB 실험 구조 사용 권장")

    return {
        "success":      True,
        "pdb_path":     pdb_path,
        "plddt_mean":   plddt,
        "version":      version,
        "predicted_at": predicted_at,
    }


# ─────────────────────────────────────────────
# DB targets 테이블 업데이트
# ─────────────────────────────────────────────
def update_target_db(conn: sqlite3.Connection, uniprot_id: str, result: dict):
    """targets 테이블의 예측 구조 관련 컬럼을 업데이트한다."""
    cur = conn.cursor()

    # 해당 uniprot_id가 DB에 있는지 확인
    row = cur.execute(
        "SELECT id FROM targets WHERE uniprot_id = ?", (uniprot_id,)
    ).fetchone()

    if row is None:
        print(f"  [DB] targets에 {uniprot_id} 없음 — 스킵")
        return

    cur.execute("""
        UPDATE targets SET
            predicted_pdb_path = ?,
            predicted_plddt    = ?,
            structure_source   = ?,
            af_version         = ?,
            af_predicted_at    = ?
        WHERE uniprot_id = ?
    """, (
        result.get("pdb_path"),
        result.get("plddt_mean"),
        "alphafold_db" if result.get("success") else "rcsb_pdb",
        result.get("version"),
        result.get("predicted_at"),
        uniprot_id,
    ))
    conn.commit()
    print(f"  [DB] {uniprot_id} 업데이트 완료")


# ─────────────────────────────────────────────
# 결과 요약 출력
# ─────────────────────────────────────────────
def print_summary(results: list[dict]):
    print("\n" + "=" * 60)
    print("  AlphaFold DB 구조 예측 결과 요약")
    print("=" * 60)
    for r in results:
        status  = "✅ 성공" if r["result"]["success"] else "❌ 실패"
        plddt   = r["result"].get("plddt_mean")
        plddt_s = f"{plddt:.1f}" if plddt else "N/A"
        version = r["result"].get("version") or "N/A"
        print(f"  {r['gene_name']:<10} ({r['uniprot_id']})  "
              f"{status}  pLDDT: {plddt_s:>6}  AlphaFold v{version}")
    print("=" * 60)

    pdb_paths = [r["result"]["pdb_path"] for r in results if r["result"]["success"]]
    if pdb_paths:
        print("\n저장된 파일:")
        for p in pdb_paths:
            print(f"  {p}")
        print("\n다음 단계:")
        print("  python scripts/prepare_targets.py  # .pdbqt 변환")
        print("  python scripts/run_docking.py       # 도킹 실행")
    print()


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="AlphaFold DB API로 단백질 구조를 다운로드합니다."
    )
    parser.add_argument(
        "--uniprot", nargs="+",
        help="처리할 UniProt ID 목록 (기본값: CHRNA1, MUSK, LRP4)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="이미 다운로드된 파일이 있어도 재다운로드"
    )
    parser.add_argument(
        "--db", default=os.path.join("data", "mg_discovery.db"),
        help="SQLite DB 경로 (기본값: data/mg_discovery.db)"
    )
    args = parser.parse_args()

    # 출력 디렉토리
    base_dir  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rel_out_dir = os.path.join("data", "structures", "predicted")
    out_dir   = os.path.join(base_dir, rel_out_dir)
    os.makedirs(out_dir, exist_ok=True)

    db_path = os.path.join(base_dir, args.db) if not os.path.isabs(args.db) else args.db

    # DB 연결 및 마이그레이션
    conn = None
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        print("[DB] 마이그레이션 확인 중...")
        migrate_db(conn)
    else:
        print(f"[경고] DB 파일 없음: {db_path} — DB 업데이트 건너뜀")

    # 처리할 타겟 목록 결정
    if args.uniprot:
        # CLI로 지정한 UniProt ID
        targets_to_process = [
            {"uniprot_id": uid, "gene_name": uid}
            for uid in args.uniprot
        ]
    else:
        # DB에서 읽기 시도 → 없으면 기본 타겟 사용
        targets_to_process = []
        if conn:
            rows = conn.execute(
                "SELECT uniprot_id, gene_name FROM targets"
            ).fetchall()
            if rows:
                targets_to_process = [
                    {"uniprot_id": r[0], "gene_name": r[1] or r[0]}
                    for r in rows
                    if r[0]
                ]
        if not targets_to_process:
            print("[정보] DB에 타겟 없음 — 기본 타겟(CHRNA1, MUSK, LRP4) 사용")
            targets_to_process = DEFAULT_TARGETS

    # 타겟별 처리
    print(f"\n총 {len(targets_to_process)}개 타겟 처리 시작...\n")
    all_results = []
    for tgt in targets_to_process:
        uniprot_id = tgt["uniprot_id"]
        gene_name  = tgt.get("gene_name", uniprot_id)

        result = process_target(
            uniprot_id=uniprot_id,
            gene_name=gene_name,
            out_dir=out_dir,
            force=args.force,
        )

        # Convert to relative path before saving to DB
        if result.get("pdb_path"):
            rel_pdb_path = os.path.relpath(result["pdb_path"], base_dir)
            # Use forward slashes for cross-platform compatibility
            result["pdb_path"] = rel_pdb_path.replace("\\", "/")

        if conn:
            update_target_db(conn, uniprot_id, result)

        all_results.append({
            "uniprot_id": uniprot_id,
            "gene_name":  gene_name,
            "result":     result,
        })

        # API rate-limit 방지
        time.sleep(0.5)

    if conn:
        conn.close()

    print_summary(all_results)


if __name__ == "__main__":
    main()
