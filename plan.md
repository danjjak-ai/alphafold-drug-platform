# Implementation Plan: MG-Repurposing AI Simulator
**중증근무력증 치료제 재창출 AI 플랫폼 구축 계획서**
*Version 2.0 | 2025 Q3 | 오픈소스 전용 · 무료 API · 로컬 실행 기준*

---

## 0. 프로젝트 전제 조건 및 시스템 요구사항

본 플랫폼은 추가 클라우드 비용 없이 로컬 환경에서 완전히 구동 가능하도록 설계되었다. 단, 아래의 하드웨어 및 소프트웨어 전제 조건을 반드시 확인해야 한다.

| 구분 | 최소 사양 | 권장 사양 | 비고 |
|---|---|---|---|
| GPU | NVIDIA GPU 8GB VRAM (ESMFold 단량체) | NVIDIA RTX 3090/4090 24GB | ESMFold 전장 단백질 예측 필수. CPU 실행 시 수십 배 느림 |
| RAM | 32 GB | 64 GB 이상 | AutoDock Vina 배치 처리, RDKit 2500개 화합물 동시 처리 |
| 저장공간 | 50 GB SSD | 200 GB NVMe SSD | 모델 체크포인트(~15GB), PDB 파일, SQLite DB 포함 |
| OS | Windows 10/11 | Ubuntu 22.04 LTS | Windows 환경에서 uv 사용 권장 |
| Package Manager | uv | ghcr.io/astral-sh/uv | 고속 패키지 관리 및 격리된 venv 환경 보장 |
| Python | 3.10 | 3.10 | PyTorch, RDKit 호환성 기반 |
| 인터넷 | 초기 실행 시 필요 | - | 초기 데이터 수집 및 모델 체크포인트 다운로드에만 필요 |

> ⚠ **주의:** GPU VRAM이 8GB 미만인 경우, ESMFold를 ColabFold (Google Colab 무료 GPU)에서 실행하고 .pdb 파일만 로컬로 다운로드하는 하이브리드 전략을 대안으로 채택할 것.

---

## Phase 0: 프로젝트 기반 설계 (신규 추가)

원본 계획에는 없었으나, 성공적인 프로젝트 수행을 위해 반드시 선행되어야 할 설계 활동들이다.

### 0.1 데이터 모델 설계 (SQLite Schema)

모든 파이프라인 단계의 데이터는 단일 SQLite 데이터베이스(`mg_discovery.db`)에 통합 저장한다.

```sql
targets         (id, uniprot_id, gene_name, sequence, pdb_id, structure_path, created_at)
compounds       (id, chembl_id, name, smiles, inchikey, mw, logp, tpsa, hbd, hba, max_phase, created_at)
docking_results (id, compound_id, target_id, vina_score, rmsd_lb, rmsd_ub, pose_path, run_timestamp)
admet_results   (id, compound_id, bbb_permeable, cyp3a4_inhibitor, herg_ic50_pred, dili_risk, oral_bioavailability, pains_flag)
activity_predictions (id, compound_id, target_id, model_type, activation_prob, binding_stability_score, confidence, run_timestamp)
validation_log  (id, compound_id, target_id, assay_type, result, source, notes)
```

### 0.2 버전 관리 및 재현성 전략

- **Git 저장소 초기화:** 모든 스크립트, 설정 파일, 데이터 수집 로직 버전 관리
- **DVC (Data Version Control):** 대용량 데이터 파일(.pdb, .pdbqt, DB)의 버전 추적 (Git LFS 대안)
- **컨테이너 기반 실행:** Docker Compose로 Python 환경, AutoDock Vina, Streamlit 서비스 격리
- **랜덤 시드 고정:** 모든 ML 모델 훈련에서 `seed=42` 전역 적용 (NumPy, PyTorch, RDKit)
- **실험 추적:** MLflow (오픈소스) 또는 Weights & Biases 무료 tier를 이용한 모델 하이퍼파라미터 및 메트릭 기록

> 💡 **전문가 노트:** 재현 불가능한 결과는 과학적 가치가 없다. 파이프라인의 모든 난수 요소에 시드를 고정하고, 실행 환경을 Docker로 캡슐화하는 것이 선택이 아닌 필수다.

---

## Phase 1: 환경 구성 및 데이터 파이프라인 (기간: 1~2주)

### 1.1 디렉터리 구조

```
mg_repurposing/
  ├── data/
  │   ├── raw/          # API 원본 데이터
  │   ├── processed/    # 전처리된 SMILES, FASTA
  │   ├── structures/   # .pdb, .pdbqt 파일
  │   └── mg_discovery.db
  ├── models/           # ML 모델 체크포인트
  ├── scripts/          # 파이프라인 스크립트
  ├── web/              # Streamlit 앱
  ├── results/          # 최종 결과물
  ├── Dockerfile
  ├── docker-compose.yml
  └── requirements.txt
```

### 1.2 requirements.txt 핵심 의존성

| 패키지 | 버전 (권장) | 용도 | 설치 주의사항 |
|---|---|---|---|
| rdkit | 2023.09+ | 분자 조작, SMILES 처리, 3D 컨포머 생성, PAINS 필터링 | `conda install -c conda-forge rdkit` 권장 (pip 설치 불안정) |
| torch | 2.1+ (CUDA 11.8) | ESMFold, EGNN 모델 실행 | CUDA 버전과 PyTorch 버전 반드시 매칭 |
| torch-geometric (PyG) | 2.4+ | GNN/EGNN 그래프 학습 프레임워크 | torch_scatter, torch_sparse 별도 설치 필요 |
| deepchem | 2.7+ | ADMET 예측, 분자 피처라이저, 기존 Drug Discovery 모델 | conda 환경 권장; pip 설치 시 의존성 충돌 자주 발생 |
| biopython | 1.81+ | FASTA 파싱, PDB 구조 조작 | pip 설치 안정적 |
| transformers | 4.35+ | ESMFold (`facebook/esmfold_v1`) 모델 로드 | esm 패키지 별도 설치 필요 |
| meeko | 0.5+ | SMILES → .pdbqt 변환 (AutoDock Vina 리간드 준비) | `pip install meeko` |
| streamlit | 1.28+ | 대시보드 웹 앱 | pip 설치 안정적 |
| stmol | 0.0.9+ | Streamlit 내 3D 분자 시각화 | py3Dmol 함께 설치 |
| langchain | 0.1+ | RAG 파이프라인 구성 | chromadb, sentence-transformers 함께 설치 |
| chromadb | 0.4+ | 벡터 데이터베이스 (RAG) | pip 설치 가능 |
| requests | 2.31+ | API 데이터 수집 | - |

### 1.3 데이터 수집 스크립트 상세 명세

#### fetch_targets.py – UniProt API

- **대상:** CHRNA1 (P02708), MuSK (O15146), LRP4 (O94898)
- **수집 항목:** FASTA 서열, 기능 어노테이션, 도메인 경계, PTM 위치, PDB 엔트리 목록
- **추가 처리:** 각 타겟의 실험적 PDB 구조 중 해상도 < 2.5Å, apo-form 구조를 RCSB API로 자동 다운로드

> ⚠ **주의:** ESMFold 예측 구조와 실험 구조(PDB) 간 RMSD를 반드시 비교하여 예측 신뢰도를 검증할 것. RMSD > 3Å인 경우 예측 구조 단독 사용 지양.

#### fetch_drugs.py – ChEMBL API

- **1차 필터링:** max_phase = 4 (FDA 승인 약물), 분자량 150~500 Da
- **2차 필터링:** Lipinski RO5 통과, TPSA < 140Å², 회전 가능 결합 수 ≤ 10
- **3차 필터링 (추가 권고):** RDKit PAINS filter 적용 → pan-assay 반응성 물질 사전 제거
- **예상 후보 수:** 전체 FDA 승인 약물 ~2,500개 → 필터링 후 약 1,800~2,000개
- **저장:** SMILES, InChIKey, ChEMBL ID, 기존 적응증 ATC 코드, max_phase SQLite 저장

> 💡 **전문가 노트:** 보조 전략으로 DrugBank XML (무료 academic 라이선스)도 병행 수집하여 ChEMBL 누락 약물 보완. 두 데이터셋은 InChIKey 기준으로 중복 제거 후 통합.

---

## Phase 2: 구조 시뮬레이션 (기간: 2~3주)

### 2.1 단백질 구조 예측 – 2단계 전략

**1단계: ESMFold 1차 구조 예측 (빠른 프로토타이핑)**

- transformers 라이브러리의 `facebook/esmfold_v1` 모델 사용
- 각 타겟의 정준(canonical) UniProt 서열 사용
- 출력: .pdb 파일 + per-residue pLDDT confidence score
- pLDDT < 70인 잔기는 구조적으로 불안정 → 결합 포켓 분석에서 제외

**2단계: AlphaFold2 (ColabFold) 고정밀 검증 (상위 후보 재도킹 시 사용)**

- ColabFold 무료 사용 (Google Colab 기반)
- MSA(Multiple Sequence Alignment) 기반 예측으로 ESMFold 대비 정확도 향상
- 복합체 예측 필요 시 AlphaFold-multimer 사용

> ⚠ **주의:** ESMFold 예측 후 반드시 PyMOL 또는 ChimeraX로 구조를 시각적으로 검토할 것. 특히 결합 포켓 주변의 루프 영역(loop region)에서 예측 오류가 빈번히 발생한다.

### 2.2 가상 스크리닝 (Virtual Screening) – 개선된 파이프라인

#### 단계 1: 리간드 준비

- RDKit으로 SMILES → 3D 컨포머 생성: ETKDG 알고리즘 + MMFF94 에너지 최소화
- 각 화합물에 대해 최소 10개 컨포머 생성, 최저 에너지 컨포머 선택
- Meeko로 .pdbqt 변환: 회전 가능 결합 및 전하 자동 처리
- PAINS 패턴이 검출된 화합물 자동 플래그 처리 (제거는 아니고 보류)

#### 단계 2: 단백질 준비

- ADFRsuite의 `prepare_receptor`를 이용한 수소 추가, 전하 할당, .pdbqt 변환
- FPOCKET를 이용한 결합 포켓 자동 탐지 및 격자 박스(grid box) 좌표 자동 설정
- 결합 포켓별로 독립적인 도킹 수행 (CHRNA1: orthosteric + allosteric, MuSK: ATP pocket + Fz-CRD)

#### 단계 3: 배치 도킹 실행

- AutoDock Vina 1.2 또는 SMINA (개선된 scoring function) 사용
- 병렬화: Python `multiprocessing`으로 CPU 코어 수 기준 병렬 실행
- 규모: 2,000개 × 3 표적 = 6,000회 도킹, 예상 소요 시간: 16코어 CPU 기준 약 12~20시간
- 출력: CSV 로그 (`compound_id`, `target_id`, `vina_score`, `rmsd_lb`, `rmsd_ub`, `pose_path`)

> 💡 **전문가 노트:** 도킹 파이프라인을 먼저 Pyridostigmine (양성 대조군)과 5~10개의 무작위 약물로 테스트 실행하여 파이프라인 자체의 정확성을 검증한 후 전체 배치를 실행할 것. 검증 없이 2,000개 배치를 돌리면 오류 발견 시 전체 재실행이 필요해진다.

### 2.3 도킹 후 처리 (Post-Docking Analysis)

- **1차 필터:** Vina score < −7.0 kcal/mol 기준 히트 선별
- **MM-GBSA 재채점:** 상위 100위 후보에 AmberTools (무료)를 이용한 MM-GBSA 재채점으로 false positive 제거
- **시각적 검증:** PyMOL 자동화 스크립트로 상위 20위 포즈를 이미지 파일로 저장
- **ADMET 필터링:** 상위 후보에 SwissADME + pkCSM (무료 웹 API) 자동 쿼리 → DB 저장

---

## Phase 3: AI 활성 예측 모델 (기간: 2~4주)

### 3.1 구현 전략 – 현실적 접근법

| 접근법 | 구현 난이도 | 예측 정확도 | 개발 기간 | 권장 단계 |
|---|---|---|---|---|
| DeepPurpose (DTI 모델) | 낮음 (3줄 코드) | 중간 (문헌 검증됨) | 1~2일 | Phase 3 즉시 적용 (베이스라인) |
| Chemprop (D-MPNN) | 낮음~중간 | 높음 (화합물 활성 예측) | 2~3일 | Phase 3 병행 사용 |
| DGraphDTA (PyG 기반) | 중간 | 높음 (단백질-리간드 친화도) | 3~5일 | Phase 3 심화 버전 |
| 커스텀 EGNN | 높음 | 최고 (커스터마이징 가능) | 2~4주 | Phase 4 이후 장기 개선 |

> 💡 **전문가 노트:** Phase 3에서는 DeepPurpose + Chemprop을 기본으로 구동하고, EGNN 커스텀 구현은 별도 R&D 브랜치에서 진행할 것을 강력히 권고. 베이스라인 없이 고급 모델에만 집중하면 성능 비교 기준이 없어 개선도 측정이 불가능하다.

### 3.2 훈련 데이터 준비

- ChEMBL에서 CHRNA1 (`CHEMBL4296141`) 및 MUSK (`CHEMBL4523582`) 관련 assay 데이터 추출
- **표준화:** IC50, Ki, EC50 등 다양한 활성 단위를 pChEMBL value (−log10 M)로 통일
- **이진 분류 기준:** pChEMBL ≥ 6 (IC50 ≤ 1μM) → Active, pChEMBL < 5 → Inactive
- **클래스 불균형 처리:** SMOTE 오버샘플링 또는 class weight 조정
- **데이터 분할:** Train/Validation/Test = 70/15/15, **scaffold split** 적용 (무작위 분할의 데이터 누출 방지)

### 3.3 성능 평가 지표

| 지표 | 계산 방법 | 목표값 | 의미 |
|---|---|---|---|
| AUROC | ROC 곡선 아래 면적 | > 0.80 | 전반적 분류 능력. 클래스 불균형에 강건 |
| AUPRC | Precision-Recall 곡선 아래 면적 | > 0.70 | 희귀 Active 화합물 발굴에 더 적합한 지표 |
| Hit Rate @ Top 1% | 상위 1% 예측 중 실제 Active 비율 | > 10× 무작위 대비 | 가상 스크리닝 실용 성능 평가 |
| Enrichment Factor (EF) | EF = (히트수/선택수) / (전체히트/전체수) | EF5% > 5 | 상위 5% 선별 시 농축 계수 |

---

## Phase 4: 대시보드 및 LLM 검증 (기간: 1~2주)

### 4.1 Streamlit 대시보드 – 상세 설계

| 페이지 | 주요 기능 | 사용 라이브러리 | 주요 시각화 |
|---|---|---|---|
| 1. 후보 순위표 | 다중 필터(표적, 점수 범위, ADMET 상태, 기존 적응증) 기반 후보 목록. CSV 내보내기 | Streamlit, pandas, plotly | 산점도 (Vina score vs. AI 활성 예측), 히스토그램 |
| 2. 3D 구조 뷰어 | 선택 화합물의 도킹 포즈 3D 렌더링. 수소결합 하이라이트. 표적 결합 부위 표면 표시 | stmol, py3Dmol | 3D 분자 인터랙티브 뷰 |
| 3. ADMET 프로파일 | 선택 화합물의 ADMET 예측 결과 방사형 차트. 규제 필터 통과/실패 시각화 | plotly, pandas | 레이더 차트, 트래픽 라이트 |
| 4. AI 설명 (LLM RAG) | 선택 화합물에 대한 MG 치료 가능성 문헌 기반 자동 설명 생성. 인용 논문 링크 제공 | langchain, chromadb, ollama | 텍스트 + 소스 인용 |
| 5. 검증 로그 | 양성/음성 대조군 도킹 결과 비교, 파이프라인 실행 이력 추적 | Streamlit, matplotlib | 시계열 차트, 비교 바 차트 |

### 4.2 LLM RAG 시스템 – 구현 가이드

#### 모델 선택

- **Ollama + llama3.2 (8B 또는 3B):** 한국어/영어 혼합 쿼리 지원, 8GB VRAM으로 구동 가능
- **대안:** Ollama + mistral:7b-instruct (영어 성능 우수) 또는 Qwen2.5:7b (한국어 성능 우수)

#### RAG 문서 소스

- **PubMed Central (PMC) Open Access:** MG 관련 오픈 액세스 논문 자동 수집 (Entrez API)
- **bioRxiv:** 최신 프리프린트 논문
- **FDA, EMA 공개 허가 문서:** 기승인 MG 치료제 심사 보고서
- **ChEMBL drug mechanism 데이터:** 화합물 기전 데이터

#### RAG 파이프라인

- **청킹:** 논문을 400 토큰 단위로 분할 (50 토큰 오버랩)
- **임베딩:** `sentence-transformers/all-MiniLM-L6-v2` (무료, 로컬 실행)
- **벡터 DB:** ChromaDB (로컬 지속 저장)
- **프롬프트 템플릿:** 약물명, 기전, MG 치료 가능성, 임상 증거, 위험성을 구조화하여 출력

> ⚠ **주의:** LLM 출력은 사실 확인(fact-checking) 없이 임상 판단에 활용하면 안 된다. 대시보드에 **'AI 생성 콘텐츠 – 전문가 검토 필요'** 면책 문구를 반드시 표시할 것.

---

## Phase 5: 검증, 품질 관리 및 결과 보고 (기간: 1~2주)

### 5.1 파이프라인 검증 (양성/음성 대조군)

| 대조군 화합물 | 표적 | 예상 결과 | 판단 기준 | 비고 |
|---|---|---|---|---|
| Pyridostigmine (양성) | AChE (간접) | 도킹 점수 < −7.5 kcal/mol | MG 표준치료제. NMJ 강화 확인 | CHRNA1 도킹이 아닌 AChE 도킹으로 테스트 |
| d-Tubocurarine (양성) | CHRNA1 (직접) | 도킹 점수 < −8.0 kcal/mol | 알려진 AChR 길항제. MIR 영역 결합 확인 | 경쟁 억제 기전 검증용 |
| Agrin-derived peptide (양성) | MuSK (직접) | 도킹 점수 < −7.0 kcal/mol | MuSK 활성화 인자. Fz-CRD 결합 검증 | 소분자가 아닌 펩타이드; 도킹 조건 조정 필요 |
| Aspirin (음성) | CHRNA1, MuSK | 도킹 점수 > −6.0 kcal/mol | MG 비관련 약물. 낮은 친화도 확인 | 파이프라인 특이성 검증 |

### 5.2 결과물 및 산출물 목록

| 산출물 | 형식 | 내용 | 대상 독자 |
|---|---|---|---|
| `mg_discovery.db` | SQLite | 전체 파이프라인 데이터 통합 DB | 개발자 / 연구자 |
| `top_candidates.csv` | CSV | 상위 50위 후보 약물 (점수, ADMET, 구조 경로 포함) | 연구자 / 의학전문가 |
| `docking_poses/` | PDB/PNG | 상위 20위 도킹 포즈 3D 구조 파일 및 이미지 | 구조 생물학자 |
| `results_report.pdf` | PDF | 방법론, 상위 10위 후보 분석, 한계점, 다음 단계 포함 최종 보고서 | 경영진 / 투자자 / 규제기관 |
| `pipeline_code/` | GitHub 저장소 | 전체 파이프라인 코드, Dockerfile, requirements.txt | 개발자 / 외부 연구자 |
| `streamlit_app/` | 웹 앱 (localhost) | 인터랙티브 대시보드 | 전체 이해관계자 |

### 5.3 최종 보고서(PDF) 필수 포함 항목

- **Executive Summary:** 비전문가 독자를 위한 1페이지 요약 (한국어)
- **방법론 요약:** 각 파이프라인 단계의 도구, 파라미터, 데이터 소스
- **상위 10위 후보 약물 프로파일:** 구조, 도킹 포즈 이미지, 점수, 기존 적응증, MG 가설 기전
- **한계점 (Limitations):** in silico 예측의 내재적 불확실성, 데이터 품질 이슈, 모델 편향
- **다음 단계 제안:** 우선순위 in vitro 검증 실험 계획, 필요 자원 및 예산
- **이해충돌 선언:** 연구 독립성 확보 문서

---

## Phase 6: 위험 관리 및 프로젝트 현실화 계획 (신규 추가)

### 6.1 주요 위험 요인 및 대응 전략

| 위험 요인 | 발생 가능성 | 영향도 | 대응 전략 |
|---|---|---|---|
| ESMFold 예측 구조 신뢰도 낮음 (pLDDT < 70) | 높음 | 높음 | pLDDT 임계값 필터 적용 + ColabFold로 교차 검증 + 실험 PDB 구조 대안 사용 |
| GPU VRAM 부족으로 ESMFold 실행 불가 | 중간 | 높음 | ColabFold (Google Colab 무료 GPU) 활용 또는 배치 크기 감소 |
| 도킹 결과의 대규모 false positive | 높음 | 중간 | MM-GBSA 재채점 적용 + 다중 독립 도킹 실행 앙상블 |
| ChEMBL 데이터 품질 이질성 (assay 비균일) | 높음 | 중간 | 데이터 표준화 파이프라인 구축 + pChEMBL value 통일 |
| Ollama LLM 한국어 성능 미흡 | 중간 | 낮음 | Qwen2.5 또는 EXAONE-3.5(LG AI) 대안 모델 사용 |
| EGNN 구현 복잡도 초과로 일정 지연 | 높음 | 중간 | DeepPurpose로 베이스라인 먼저 확보, EGNN은 별도 R&D 브랜치 분리 |
| 파이프라인 재현 불가 (seed, 버전 불일치) | 중간 | 높음 | DVC + Docker + MLflow 조합으로 완전 재현 환경 구축 |

### 6.2 전체 프로젝트 구현 현황 요약 (Status)

| Phase | 마일스톤 | 현 상태 | 구현 항목 |
|---|---|---|---|
| Phase 1 | 환경/데이터 파이프라인 | **완료** | `fetch_targets.py`, `fetch_drugs.py`, `init_db.py` |
| Phase 2 | 구조 예측 및 1차 도킹 | **완료** | `predict_structures.py`, `run_docking.py`, `vina_bin/` |
| Phase 3 | AI 활성 예측 모델 | **완료** | `train_ai_model.py`, `predict_activity.py` |
| Phase 4 | 분석 대시보드 | **부분 완료** | `web/app.py` (LLM RAG - **미구현**) |
| Phase 5 | 정밀 검증 (MM-GBSA) | **미구현** | AmberTools 기반 재채점 파이프라인 |
| Phase 6 | 결과 보고서 자동화 | **미구현** | PDF 리포트 생성 스크립트 |

---

*본 계획서는 살아있는 문서(Living Document)이며, 각 Phase 완료 시 결과를 반영하여 업데이트한다.*
