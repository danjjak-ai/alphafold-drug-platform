import requests
import os
import sqlite3
import numpy as np
from rdkit import Chem

# ─────────────────────────────────────────────────────
# AlphaFold 예측 구조 우선 사용 헬퍼
# ─────────────────────────────────────────────────────
PREDICTED_DIR = os.path.join("data", "structures", "predicted")

def get_best_pdb_path(gene_name: str, fallback_rcsb_path: str) -> tuple[str, str]:
    """
    AlphaFold DB 예측 구조가 있으면 우선 사용하고,
    없으면 RCSB 실험 구조로 폴백한다.

    반환값: (사용할 pdb 경로, 출처 문자열)
    """
    predicted_pdb = os.path.join(PREDICTED_DIR, f"{gene_name.lower()}_alphafold.pdb")
    if os.path.exists(predicted_pdb):
        print(f"  [구조 출처] AlphaFold DB 예측 구조 사용: {predicted_pdb}")
        return predicted_pdb, "alphafold_db"
    print(f"  [구조 출처] RCSB 실험 구조 사용: {fallback_rcsb_path}")
    return fallback_rcsb_path, "rcsb_pdb"

def update_structure_source(db_path: str, gene_name: str, source: str, pdbqt_path: str):
    """targets 테이블의 structure_source와 structure_path를 갱신한다."""
    if not os.path.exists(db_path):
        return
    try:
        conn = sqlite3.connect(db_path)
        # structure_source 컬럼이 없으면 추가 (마이그레이션)
        existing = {r[1] for r in conn.execute("PRAGMA table_info(targets)").fetchall()}
        if "structure_source" not in existing:
            conn.execute("ALTER TABLE targets ADD COLUMN structure_source TEXT DEFAULT 'rcsb_pdb'")
        conn.execute(
            "UPDATE targets SET structure_path = ?, structure_source = ? WHERE gene_name = ?",
            (pdbqt_path, source, gene_name)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"  [DB 갱신 오류] {e}")

def download_pdb(pdb_id, output_path):
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        return True
    return False

def save_receptor_pdbqt(mol, output_path):
    # Simple manual PDBQT writer for rigid receptors
    conf = mol.GetConformer()
    with open(output_path, "w", encoding="utf-8") as f:
        for atom in mol.GetAtoms():
            idx = atom.GetIdx()
            pos = conf.GetAtomPosition(idx)
            info = atom.GetPDBResidueInfo()
            
            name = info.GetName() if info else f" {atom.GetSymbol():<3}"
            res_name = info.GetResidueName() if info else "UNK"
            chain = info.GetChainId() if info else "A"
            res_num = info.GetResidueNumber() if info else 1
            symbol = atom.GetSymbol().upper()
            
            # Map symbol to AutoDock types
            ad_type = symbol
            if symbol == "H":
                neighbors = atom.GetNeighbors()
                if neighbors and neighbors[0].GetSymbol() in ["O", "N", "S"]:
                    ad_type = "HD"
                else:
                    ad_type = "H"
            elif symbol == "O": ad_type = "OA"
            elif symbol == "N": ad_type = "NA"
            
            # ATOM card format
            line = f"ATOM  {idx+1:>5} {name:<4} {res_name:>3} {chain}{res_num:>4}    "
            line += f"{pos.x:>8.3f}{pos.y:>8.3f}{pos.z:>8.3f}"
            line += f"  1.00  0.00    +0.000 {ad_type:<2}\n"
            f.write(line)
        f.write("TER\n")
    return True

def process_target(pdb_raw, pdbqt_out, chain_ids=None):
    mol = Chem.MolFromPDBFile(pdb_raw, removeHs=False)
    if mol is None:
        return False
    
    if chain_ids:
        rw_mol = Chem.RWMol(mol)
        for atom in reversed(range(rw_mol.GetNumAtoms())):
            res_info = rw_mol.GetAtomWithIdx(atom).GetPDBResidueInfo()
            if res_info is None or res_info.GetChainId().strip() not in chain_ids:
                rw_mol.RemoveAtom(atom)
        mol = rw_mol.GetMol()

    # Add Hs
    mol = Chem.AddHs(mol, addCoords=True)
    
    # Calculate Center
    conf = mol.GetConformer()
    pts = conf.GetPositions()
    center = pts.mean(axis=0)
    print(f"Receptor {pdbqt_out} Center: {center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}")
    
    return save_receptor_pdbqt(mol, pdbqt_out)

if __name__ == "__main__":
    targets_out_dir = os.path.join("data", "structures", "targets")
    os.makedirs(targets_out_dir, exist_ok=True)
    db_path = os.path.join("data", "mg_discovery.db")

    # ── CHRNA1 ────────────────────────────────────────────
    print("Preparing CHRNA1 receptor...")
    chrna1_pdb, chrna1_src = get_best_pdb_path(
        "chrna1",
        fallback_rcsb_path="data/structures/targets/7ql6_raw.pdb"
    )
    if chrna1_src == "rcsb_pdb" and not os.path.exists(chrna1_pdb):
        download_pdb("7QL6", chrna1_pdb)
    chrna1_pdbqt = os.path.join(targets_out_dir, "chrna1.pdbqt")
    ok = process_target(chrna1_pdb, chrna1_pdbqt, chain_ids=['A', 'D'] if chrna1_src == "rcsb_pdb" else None)
    if ok:
        update_structure_source(db_path, "CHRNA1", chrna1_src, chrna1_pdbqt)

    # ── MuSK ─────────────────────────────────────────────
    print("Preparing MuSK receptor...")
    musk_pdb, musk_src = get_best_pdb_path(
        "musk",
        fallback_rcsb_path="data/structures/targets/8s9p_raw.pdb"
    )
    if musk_src == "rcsb_pdb" and not os.path.exists(musk_pdb):
        download_pdb("8S9P", musk_pdb)
    musk_pdbqt = os.path.join(targets_out_dir, "musk.pdbqt")
    ok = process_target(musk_pdb, musk_pdbqt, chain_ids=['C'] if musk_src == "rcsb_pdb" else None)
    if ok:
        update_structure_source(db_path, "MUSK", musk_src, musk_pdbqt)

    # ── LRP4 ─────────────────────────────────────────────
    print("Preparing LRP4 receptor...")
    lrp4_pdb, lrp4_src = get_best_pdb_path(
        "lrp4",
        fallback_rcsb_path="data/structures/targets/8s9p_raw.pdb"
    )
    if lrp4_src == "rcsb_pdb" and not os.path.exists(lrp4_pdb):
        # 8S9P는 MuSK 준비 단계에서 이미 다운로드됨
        if not os.path.exists(lrp4_pdb):
            download_pdb("8S9P", lrp4_pdb)
    lrp4_pdbqt = os.path.join(targets_out_dir, "lrp4.pdbqt")
    ok = process_target(lrp4_pdb, lrp4_pdbqt, chain_ids=['B'] if lrp4_src == "rcsb_pdb" else None)
    if ok:
        update_structure_source(db_path, "LRP4", lrp4_src, lrp4_pdbqt)

    print("\nTarget preparation complete.")
    print("TIP: AlphaFold DB 구조를 사용하려면 먼저 아래를 실행하세요:")
    print("  python scripts/predict_structures.py")
