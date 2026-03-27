# 🧬 AlphaFold Drug Platform — Technical Component 일람

> 생성일: 2026-03-24  
> 프로젝트: `alphafold-drug-platform`

---

## 1. 인프라 / 런타임

| 구분 | 현재 사용 | 버전 | 용도 | 동일 기능 대안 |
|------|-----------|------|------|----------------|
| **Python** | Python | 3.10 (Dockerfile `python:3.10-slim`) | 전체 백엔드 런타임 | Python 3.11/3.12, Conda |
| **패키지 관리자** | uv | latest (`ghcr.io/astral-sh/uv`) | 고속 pip 대체 의존성 설치 | pip, poetry, conda |
| **컨테이너** | Docker | (Dockerfile 기반) | Cloud Run 배포 | Podman, buildah |
| **배포 플랫폼** | Google Cloud Run | — | 서버리스 컨테이너 호스팅 | AWS App Runner, Azure Container Apps |

---

## 2. 웹 프레임워크 / UI 백엔드

| 구분 | 현재 사용 | 버전 | 용도 | 연결 / CDN | 동일 기능 대안 |
|------|-----------|------|------|------------|----------------|
| **앱 서버** | Streamlit | ≥1.x (`requirements.txt`) | Python 기반 대시보드 서버 | `streamlit run web/app.py` | Gradio, Dash (Plotly), Panel |
| **Streamlit 분자 뷰어** | stmol | ≥0.x | Streamlit 내 3Dmol 래퍼 | PyPI | py3Dmol (대체 가능) |
| **커스텀 컴포넌트** | Streamlit Components API | — | `web/frontend/index.html`을 iframe으로 임베드 | `components.declare_component()` | 없음 (Streamlit 전용 기능) |

---

## 3. 프론트엔드 (HTML/JS/CSS)

| 구분 | 현재 사용 | 버전 | 용도 | CDN URL | 동일 기능 대안 |
|------|-----------|------|------|---------|----------------|
| **CSS 프레임워크** | Tailwind CSS | CDN (v3) | 유틸리티 기반 스타일링 | `https://cdn.tailwindcss.com?plugins=forms,container-queries` | Bootstrap 5, UnoCSS, Bulma |
| **폰트 — 본문** | Google Fonts / Inter | Variable | UI 본문 폰트 | `https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700` | 로컬 Inter, Geist, Roboto |
| **아이콘** | Material Symbols Outlined | Variable (wght,FILL) | UI 아이콘 | `https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined` | Font Awesome 6, Heroicons, Lucide |
| **3D 분자 뷰어** | 3Dmol.js | latest (`3Dmol-min.js`) | 단백질·리간드 3D 렌더링 | `https://3Dmol.org/build/3Dmol-min.js` | NGL Viewer, Mol\*, RCSB Mol\* |
| **Streamlit 통신 브릿지** | Streamlit JS Bridge | — | `Streamlit.setComponentValue()` / `onRender()` | (Streamlit 내장) | — |

---

## 4. 화학정보학 (Cheminformatics)

| 구분 | 현재 사용 | 버전 | 용도 | 연결 방식 | 동일 기능 대안 |
|------|-----------|------|------|----------|----------------|
| **분자 처리** | RDKit | ≥2023.x (`rdkit`) | SMILES 파싱, 분자 기술자, 3D 구조 생성, 핑거프린트 | PyPI | OpenBabel, RDKit-stubs, ChemPy |
| **리간드 PDBQT 변환** | Meeko | ≥0.7.1 (`meeko`) | RDKit Mol → PDBQT 변환 (AutoDock용) | PyPI | OpenBabel CLI (`obabel`), ADFR Suite |
| **ChEMBL 데이터 접근** | chembl_webresource_client | ≥0.10.x | ChEMBL REST API 클라이언트 | PyPI / `https://www.ebi.ac.uk/chembl/api/` | PubChemPy, chembl-api |
| **단백질 구조 다운로드** | RCSB PDB HTTP API | — | PDB 파일 다운로드 | `https://files.rcsb.org/download/{PDB_ID}.pdb` | AlphaFold DB, wwPDB FTP |

---

## 5. 분자 도킹 엔진

| 구분 | 현재 사용 | 버전 | 용도 | 실행 방식 | 동일 기능 대안 |
|------|-----------|------|------|----------|----------------|
| **도킹 엔진** | AutoDock Vina | 1.2.5 (바이너리: `vina_1.2.5_linux_x86_64`) | 단백질-리간드 도킹 스코어링 | `subprocess` 호출, 결과 PDBQT | **Gnina** (CNN 기반), **GOLD**, **Glide** (Schrödinger), **rDock** |
| **병렬 도킹 실행** | Python `multiprocessing.Pool` | 표준 라이브러리 | 4-worker 병렬 도킹 | `Pool(4).imap()` | `concurrent.futures`, Dask, Ray |

---

## 6. AI / 머신러닝

| 구분 | 현재 사용 | 버전 | 용도 | 연결 방식 | 동일 기능 대안 |
|------|-----------|------|------|----------|----------------|
| **딥러닝 프레임워크** | PyTorch | ≥2.x (`torch`, `torchvision`, `torchaudio`) | GCN 모델 학습·추론 기반 | PyPI | TensorFlow, JAX |
| **그래프 신경망** | PyTorch Geometric | ≥2.x (`torch-geometric`) | 분자 그래프 구조 처리 | PyPI | DGL (Deep Graph Library) |
| **분자 ML 파이프라인** | DeepChem | ≥2.7.x (`deepchem`) | `GCNModel`, `MolGraphConvFeaturizer`, 데이터셋 처리 | PyPI | chemprop, GROVER, MolBERT |
| **트랜스포머 / NLP** | HuggingFace Transformers | ≥4.x (`transformers`) | 분자·단백질 언어 모델 활용 | PyPI | ESM (Meta), OpenMM |
| **전통 ML** | scikit-learn | ≥1.x (`scikit-learn`) | RandomForestRegressor, 데이터 분할, 평가 지표 | PyPI | XGBoost, LightGBM, CatBoost |
| **수치 계산** | NumPy | ≥1.24 (`numpy`) | 배열 연산, 핑거프린트 변환 | PyPI | CuPy (GPU), JAX numpy |
| **데이터 처리** | Pandas | ≥2.x (`pandas`) | DB 결과 처리, CSV 읽기/쓰기 | PyPI | Polars, DuckDB |
| **모델 직렬화** | joblib | 표준 (`joblib`) | sklearn 모델 저장/로드 (`.pkl`) | PyPI | pickle, ONNX Runtime |

---

## 7. RAG / LLM / 벡터 DB (구현 예정)

| 구분 | 현재 사용 | 버전 | 용도 | 연결 방식 | 동일 기능 대안 |
|------|-----------|------|------|----------|----------------|
| **LLM 오케스트레이션** | LangChain | ≥0.1.x | (도입 예정) 연구 문서 RAG | PyPI | LlamaIndex, Haystack |
| **벡터 데이터베이스** | ChromaDB | ≥0.4.x | (도입 예정) 임베딩 저장 | PyPI | Qdrant, FAISS |

---

## 8. 데이터베이스

| 구분 | 현재 사용 | 버전 | 용도 | 연결 방식 | 동일 기능 대안 |
|------|-----------|------|------|----------|----------------|
| **관계형 DB** | SQLite | 3.x (표준 `sqlite3`) | 화합물, 타겟, 도킹 결과, MD 이력 저장 (`mg_discovery.db`) | 로컬 파일 (`sqlite3.connect()`) | PostgreSQL, MySQL, DuckDB |

**SQLite 테이블 목록:**

| 테이블명 | 내용 |
|----------|------|
| `compounds` | ChEMBL 화합물 메타데이터 (SMILES, MW, LogP 등) |
| `targets` | 단백질 타겟 정보 (UniProt ID, gene_name) |
| `docking_results` | Vina 스코어, PDBQT 경로 |
| `activity_predictions` | RandomForest 예측 활성도 |
| `molecular_dynamics` | MD 시뮬레이션 이력 (RMSD, duration, frames) |

---

## 9. 시각화 / 플로팅

| 구분 | 현재 사용 | 버전 | 용도 | 동일 기능 대안 |
|------|-----------|------|------|----------------|
| **데이터 시각화** | Matplotlib | ≥3.7.x (`matplotlib`) | 정적 차트, RMSD 플롯 | Seaborn, Bokeh |
| **인터랙티브 시각화** | Plotly | ≥5.x (`plotly`) | 인터랙티브 그래프 | Bokeh, Altair, Vega-Lite |
| **RMSD 차트** | Inline SVG (Custom) | — | MD 페이지 RMSD 시계열 오버레이 | Chart.js, D3.js |

---

## 10. 유틸리티 / 기타

| 구분 | 현재 사용 | 버전 | 용도 | 동일 기능 대안 |
|------|-----------|------|------|----------------|
| **진행률 바** | tqdm | ≥4.65.x (`tqdm`) | 도킹·전처리 루프 진행률 표시 | rich (progress), alive-progress |
| **데이터 검증** | Pydantic | ≥2.x (`pydantic`) | 설정·데이터 모델 타입 검증 | attrs, dataclasses |
| **환경 변수** | python-dotenv | ≥1.x (`python-dotenv`) | `.env` 파일 로드 | dynaconf, python-decouple |
| **HTTP 클라이언트** | requests | ≥2.31.x (`requests`) | PDB 다운로드, 외부 API 호출 | httpx, aiohttp |
| **바이오인포매틱스** | Biopython | ≥1.81.x (`biopython`) | PDB 파일 파싱, 서열 처리 | MDAnalysis, ProDy |
| **과학 계산** | SciPy | ≥1.11.x (`scipy`) | 통계, 보간, 신호 처리 | statsmodels |
| **Jupyter 지원** | ipykernel | ≥6.x (`ipykernel`) | Notebook 실행 환경 | 표준 Jupyter kernel |

---

## 11. 외부 API / 데이터 소스

| 서비스 | 용도 | URL | 인증 | 대안 |
|--------|------|-----|------|------|
| **ChEMBL REST API** | 화합물·활성도 데이터 조회 | `https://www.ebi.ac.uk/chembl/api/data/` | 불필요 (공개) | PubChem API, ZINC DB |
| **RCSB PDB** | 단백질 3D 구조 다운로드 | `https://files.rcsb.org/download/{ID}.pdb` | 불필요 (공개) | AlphaFold DB, PDBe API |
| **Google Fonts API** | Inter 폰트, Material Symbols 폰트 아이콘 | `https://fonts.googleapis.com/` | 불필요 (공개) | 자가 호스팅 폰트, Adobe Fonts |
| **Tailwind CSS CDN** | CSS 프레임워크 | `https://cdn.tailwindcss.com` | 불필요 (공개) | 로컬 빌드 (`npm run build`) |
| **3Dmol.js CDN** | 분자 3D 뷰어 JS 라이브러리 | `https://3Dmol.org/build/3Dmol-min.js` | 불필요 (공개) | NGL (npm), Mol\* (npm) |

---

## 12. 버전 확인 방법

프로젝트 가상환경(`.venv`) 내에서 아래 명령으로 실제 설치된 버전을 확인할 수 있습니다:

```bash
# 전체 라이브러리 버전 확인
uv pip list

# 특정 라이브러리 확인
uv pip show streamlit rdkit deepchem langchain chromadb
```

---

*이 문서는 `requirements.txt`, `Dockerfile`, `scripts/`, `web/` 소스코드를 종합 분석하여 작성되었습니다.*
