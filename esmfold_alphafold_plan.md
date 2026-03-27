# ESMFold / AlphaFold 구조 예측 구현 플랜

> 작성일: 2026-03-24  
> 목표: 현재 RCSB 실험 구조에 의존하는 파이프라인에 **AI 기반 단백질 구조 예측** 기능을 추가한다.  
> 원칙: **기존 코드를 변경하지 않고** 새 스크립트(`predict_structures.py`)를 추가한다.

---

## 전략 개요 — 2단계 접근법

```
FASTA 서열 (UniProt)
        │
   [Stage 1]  ESMFold  ← 로컬 / HuggingFace Hub
        │       빠름 (~30s/단백질), GPU 8GB+
        │       출력: .pdb + pLDDT confidence
        ↓
  pLDDT ≥ 70? ── No ──→ ColabFold API (Stage 2)
        │                또는 AlphaFold DB 폴백
       Yes
        ↓
  .pdbqt 변환 (RDKit / Meeko 방식 유지)
        ↓
  AutoDock Vina 도킹 (기존 파이프라인과 동일)
```

---

## Phase 1 — ESMFold 로컬 실행 (우선 구현)

### 1-1. 전제 조건 및 환경

| 항목 | 요구사항 |
|------|---------|
| GPU VRAM | **8GB 이상** (NVIDIA GPU) |
| RAM | 16GB 이상 |
| 추가 패키지 | `transformers`, `accelerate`, `torch` (이미 requirements.txt에 있음) |
| 모델 크기 | `facebook/esmfold_v1` → 약 **15GB** (최초 다운로드 시) |
| 최초 실행 시간 | 약 10~30분 (모델 다운로드) |

> 💡 **GPU 없는 경우**: ESMFold는 CPU에서도 동작하지만 **단백질 1개당 10~30분** 소요됨.  
> 이 경우 아래 Phase 3 (AlphaFold DB API 폴백)를 우선 사용 권장.

### 1-2. 새 스크립트: `scripts/predict_structures.py`

**구현 내용:**
```python
# 핵심 로직 흐름 (의사코드)
from transformers import EsmForProteinFolding, AutoTokenizer
import torch

TARGETS = {
    "CHRNA1": {"uniprot": "P02708", "fasta": "..."},
    "MUSK":   {"uniprot": "O15146", "fasta": "..."},
    "LRP4":   {"uniprot": "O94898", "fasta": "..."},
}

def predict_with_esmfold(sequence: str) -> dict:
    """
    반환값:
      - pdb_string: str        (예측 PDB 구조)
      - plddt_mean: float      (평균 신뢰도)
      - plddt_per_residue: list (잔기별 신뢰도)
    """
    tokenizer = AutoTokenizer.from_pretrained("facebook/esmfold_v1")
    model = EsmForProteinFolding.from_pretrained(
        "facebook/esmfold_v1",
        low_cpu_mem_usage=True
    )
    model = model.cuda()  # GPU 사용
    model.esm = model.esm.half()  # fp16으로 VRAM 절약

    inputs = tokenizer(sequence, return_tensors="pt").to("cuda")
    with torch.no_grad():
        outputs = model(**inputs)

    pdb_str = model.output_to_pdb(outputs)[0]
    plddt   = outputs.plddt[0].mean().item()
    return {"pdb_string": pdb_str, "plddt_mean": plddt, ...}
```

### 1-3. DB 연동

`targets` 테이블에 컬럼 추가:

```sql
ALTER TABLE targets ADD COLUMN esmfold_pdb_path TEXT;
ALTER TABLE targets ADD COLUMN esmfold_plddt    REAL;
ALTER TABLE targets ADD COLUMN structure_source TEXT DEFAULT 'rcsb_pdb';
-- structure_source: 'rcsb_pdb' | 'esmfold' | 'alphafold_db' | 'colabfold'
```

### 1-4. pLDDT 기반 신뢰도 필터링

```
pLDDT ≥ 90  → 실험 구조 수준. 도킹에 바로 사용
pLDDT 70-90 → 전반적으로 신뢰. 도킹에 사용 (대부분의 경우)
pLDDT 50-70 → 불안정한 영역 존재. 결합 포켓만 재확인 후 사용
pLDDT < 50  → 신뢰 불가. 폴백(AlphaFold DB / RCSB) 사용
```

---

## Phase 2 — AlphaFold DB API 폴백 (빠른 대안)

ESMFold 실패 또는 pLDDT 낮을 경우 **DeepMind AlphaFold DB**에서 사전 계산된 구조를 자동으로 가져온다.  
**GPU 불필요 / 무료 공개 API**.

### 2-1. AlphaFold DB REST API

```
엔드포인트: https://alphafold.ebi.ac.uk/api/prediction/{UniProt_ID}

응답 예시:
{
  "pdbUrl": "https://alphafold.ebi.ac.uk/files/AF-P02708-F1-model_v4.pdb",
  "cifUrl": "...",
  "paeImageUrl": "...",
  "confidenceUrl": "..."
}
```

### 2-2. 구현 코드 (fetch_alphafold_structure)

```python
import requests

def fetch_alphafold_db(uniprot_id: str, output_path: str) -> bool:
    """AlphaFold DB에서 PDB 파일 다운로드."""
    api_url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
    resp = requests.get(api_url, timeout=30)
    if resp.status_code != 200:
        return False
    
    pdb_url = resp.json()[0]["pdbUrl"]
    pdb_resp = requests.get(pdb_url, timeout=60)
    if pdb_resp.status_code == 200:
        with open(output_path, "w") as f:
            f.write(pdb_resp.text)
        return True
    return False
```

**장점:**
- GPU 불필요, 즉시 사용 가능
- AlphaFold2 수준의 정확도 (사전 계산)
- CHRNA1, MuSK, LRP4 모두 AlphaFold DB에 존재

**단점:**
- 최신 서열 업데이트 반영이 느림
- 변이체(mutant) 구조 예측 불가

---

## Phase 3 — ColabFold (고정밀 / 복합체 예측)

최상위 도킹 후보 상위 20위에 한해 AlphaFold2 수준 정밀도로 재예측한다.

### 3-1. 두 가지 실행 방법

#### 방법 A: ColabFold API (로컬 서버 없이 사용)
```bash
pip install colabfold[alphafold]
colabfold_batch --use-gpu-relax targets.fasta results/structures/
```

#### 방법 B: Google Colab (무료 T4 GPU)
- `colabfold_batch` Colab 노트북을 실행
- 결과 `.pdb` 파일을 로컬로 다운로드
- `predict_structures.py`에서 파일 경로 등록

### 3-2. AlphaFold-multimer (복합체 예측)
LRP4-MuSK 복합체처럼 **두 단백질의 결합 구조**가 필요한 경우:
```bash
# ColabFold Multimer 사용
colabfold_batch --model-type alphafold2_multimer_v3 \
    musk_lrp4_complex.fasta results/structures/
```

---

## Phase 4 — 기존 파이프라인 통합

### 4-1. `prepare_targets.py` 수정 계획

현재 흐름:
```
RCSB .pdb 다운로드 → .pdbqt 변환
```

수정 후 흐름:
```
predict_structures.py 실행
    │
    ├─ AlphaFold DB에서 .pdb 다운로드 (즉시)
    ├─ ESMFold로 .pdb 예측 (GPU 있는 경우)
    └─ pLDDT 필터링 후 최적 구조 선택
    │
prepare_targets.py (.pdb → .pdbqt 변환) ← 기존 코드 그대로 유지
    │
run_docking.py ← 기존 코드 그대로 유지
```

### 4-2. Dashboard 연동

`web/app.py`에 구조 출처 표시 추가:
```
Current Complex 카드에:
  [구조 출처] RCSB PDB | ESMFold (pLDDT: 87.3) | AlphaFold DB v4
```

---

## 구현 우선순위 로드맵

```
Week 1  ── Phase 2: AlphaFold DB API 폴백 구현 (GPU 불필요, 즉시 가능)
              scripts/predict_structures.py (alphafold_db 모드)
              targets 테이블 컬럼 추가

Week 2  ── Phase 1: ESMFold 로컬 실행 구현 (GPU 환경 시)
              fp16 최적화, 배치 처리, pLDDT 필터링

Week 3  ── Phase 4: 기존 파이프라인 통합
              prepare_targets.py와의 연결
              dashboard 구조 출처 표시

Week 4  ── Phase 3: ColabFold 고정밀 검증 (선택적)
              상위 20개 후보 대상 재예측
```

---

## 예상 결과물

| 파일 | 내용 |
|------|------|
| `scripts/predict_structures.py` | 신규 스크립트 (AlphaFold DB + ESMFold) |
| `data/structures/predicted/CHRNA1_esmfold.pdb` | ESMFold 예측 구조 |
| `data/structures/predicted/CHRNA1_alphafold.pdb` | AlphaFold DB 구조 |
| `data/structures/predicted/CHRNA1_plddt.json` | 잔기별 신뢰도 데이터 |
| `data/mg_discovery.db` | targets 테이블에 구조 출처 컬럼 추가 |

---

## 기술 스택 비교 요약

| 방법 | GPU 필요 | 정확도 | 속도 | 비용 | 구현 난이도 |
|------|----------|--------|------|------|-------------|
| **AlphaFold DB API** | ❌ | ⭐⭐⭐⭐ | 매우 빠름 (~5s) | 무료 | ⭐ (쉬움) |
| **ESMFold (로컬)** | ✅ 8GB+ | ⭐⭐⭐ | 빠름 (~30s) | 무료 | ⭐⭐ |
| **ColabFold (로컬)** | ✅ 선택적 | ⭐⭐⭐⭐⭐ | 느림 (~10분) | 무료 | ⭐⭐⭐ |
| **AlphaFold2 (공식)** | ✅ 40GB+ | ⭐⭐⭐⭐⭐ | 매우 느림 | 무료 | ⭐⭐⭐⭐⭐ |
| **Boltz-1 (MIT)** | ✅ 8GB+ | ⭐⭐⭐⭐⭐ | 빠름 | 무료 | ⭐⭐⭐ |

> 💡 **권장 전략**: AlphaFold DB API(즉시 구현) → ESMFold(GPU 있을 때 추가) → Boltz-1(최신 고성능 대안) 순으로 단계적 도입.
