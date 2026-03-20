<div align="center">

<img src="https://github.com/danjjak-ai/alphafold-drug-platform/blob/master/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202026-03-20%20151436.png" alt="screenImage"/>

<img src="https://img.shields.io/badge/-%F0%9F%A7%AC%20RareTarget%20Discovery-1D9E75?style=for-the-badge&labelColor=085041" alt="RareTarget Discovery"/>


### AI-Powered Drug Repurposing for Rare Neuromuscular Disease

**[한국어](#한국어) · [English](#english) · [日本語](#日本語)**

---

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1+-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org)
[![RDKit](https://img.shields.io/badge/RDKit-2023.09+-1D9E75?style=flat-square)](https://www.rdkit.org)
[![AutoDock Vina](https://img.shields.io/badge/AutoDock_Vina-1.2+-FF6B35?style=flat-square)](https://vina.scripps.edu)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-F59E0B?style=flat-square)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Status-Prototype-6366F1?style=flat-square)]()

</div>

---

# 한국어

## 개요

**RareTarget Discovery**는 신경근 자가면역 희귀질환(Neuromuscular Autoimmune Disease, NAD) 치료를 위한 기존 약물 재창출(Drug Repurposing) 후보를 발굴하는 완전 오픈소스 AI 파이프라인입니다.

대상 질환은 자가항체가 신경근 접합부(NMJ)의 핵심 수용체 단백질을 공격하여 근력 약화를 유발하는 만성 희귀질환으로, 전체 환자의 약 10~15%가 현재 승인된 치료제에 반응하지 않는 **치료 저항성(Refractory)** 상태에 놓여 있습니다.

> ⚠️ 본 플랫폼은 **순수 in silico 연구 도구**입니다. 임상적 판단이나 진단에 사용할 수 없습니다.

### 신약 개발 vs 약물 재창출

| 구분 | 신약 개발 | 약물 재창출 |
|:--|:--|:--|
| ⏱ 개발 기간 | 10~15년 | **2~5년** |
| 💰 비용 | $1B~2.5B+ | **$50M~300M** |
| 🛡 안전성 데이터 | 완전 미지 | **기존 임상 데이터 존재** |
| 📋 IND 신청 | 신규 GLP 독성시험 필요 | **기존 독성 데이터 활용 가능** |

## 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                   RareTarget Pipeline                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📡 UniProt API ──┐                                     │
│  💊 ChEMBL API  ──┼──→  데이터 수집 & 전처리             │
│  🏛 DrugBank    ──┘       (FASTA + SMILES ~2,000개)     │
│                                   │                     │
│            ┌──────────────────────┤                     │
│            ▼                      ▼                     │
│  🧬 구조 예측                 💊 리간드 준비             │
│  ESMFold / AlphaFold2         RDKit + Meeko             │
│            │                      │                     │
│            └──────────┬───────────┘                     │
│                       ▼                                 │
│            ⚙️  AutoDock Vina 도킹                       │
│               (6,000+ 배치 도킹 실행)                    │
│                       │                                 │
│          ┌────────────┼────────────┐                    │
│          ▼            ▼            ▼                    │
│    🤖 AI 활성 예측  📊 MM-GBSA   🧪 ADMET               │
│    DeepPurpose/EGNN  재채점      필터링                  │
│          │            │            │                    │
│          └────────────┼────────────┘                    │
│                       ▼                                 │
│          🖥️  Streamlit Dashboard                        │
│          3D 뷰어 · ADMET 차트 · LLM RAG 설명            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 설치 및 실행

### 시스템 요구사항

| 구분 | 최소 | 권장 |
|:--|:--|:--|
| 🎮 GPU | NVIDIA 8GB VRAM | RTX 3090/4090 24GB |
| 🧠 RAM | 32 GB | 64 GB |
| 💾 저장공간 | 50 GB SSD | 200 GB NVMe |
| 🐧 OS | Ubuntu 20.04 LTS | Ubuntu 22.04 LTS |

> 💡 GPU VRAM 부족 시 [ColabFold](https://colab.research.google.com/github/sokrypton/ColabFold)에서 구조 예측 후 `.pdb` 파일만 로컬에 저장하는 하이브리드 전략을 권장합니다.

### Docker (권장)

```bash
git clone https://github.com/your-org/raretarget-discovery.git
cd raretarget-discovery
docker compose up --build
```

### 로컬 직접 설치

```bash
conda create -n raretarget python=3.10 && conda activate raretarget
conda install -c conda-forge rdkit
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cu118
pip install torch-geometric torch-scatter torch-sparse
pip install -r requirements.txt

# LLM RAG 사용 시
curl -fsSL https://ollama.com/install.sh | sh && ollama pull llama3.2
```

## 파이프라인 실행

```bash
python scripts/fetch_targets.py        # 🧬 단백질 서열 수집 (UniProt)
python scripts/fetch_drugs.py          # 💊 FDA 승인 약물 수집 (ChEMBL)
python scripts/predict_structures.py   # 🔬 3D 구조 예측 (ESMFold)
python scripts/run_docking.py          # ⚙️  배치 도킹 (AutoDock Vina)
python scripts/predict_activity.py     # 🤖 AI 활성 예측 (DeepPurpose)
python scripts/run_admet.py            # 🧪 ADMET 필터링
streamlit run web/app.py               # 🖥️  대시보드 실행 → localhost:8501

# 파이프라인 검증 (양성 대조군)
python scripts/validate_pipeline.py --control positive_ctrl
```

## 핵심 파라미터

**도킹 기준 (AutoDock Vina)**

| 결합 친화도 | 판정 |
|:--|:--|
| `< −8.0 kcal/mol` | ✅ Hit — 상위 후보 |
| `−6.0 ~ −8.0 kcal/mol` | 🔍 검토 필요 |
| `> −6.0 kcal/mol` | ❌ 폐기 |

> 상위 100위 후보는 MM-GBSA 재채점 (AmberTools, 무료) 으로 false positive를 추가 제거합니다.

**ADMET 필터**

| 항목 | 기준 | 비고 |
|:--|:--|:--|
| BBB 투과성 | logBB < −1 선호 | 말초 NMJ 표적, CNS 부작용 최소화 |
| hERG 독성 | IC50 > 10 μM | 심장 합병증 동반 환자 多 |
| DILI | 예측 음성 | 장기 병용 투여 고려 |
| PAINS | 패턴 없음 | false-positive 도킹 방지 |

## 프로젝트 구조

```
raretarget-discovery/
├── 📂 data/
│   ├── raw/               # API 원본 데이터
│   ├── processed/         # 전처리 SMILES, FASTA
│   ├── structures/        # .pdb, .pdbqt
│   └── discovery.db       # SQLite 통합 DB
├── 📂 scripts/            # 파이프라인 스크립트
├── 📂 models/egnn/        # 커스텀 EGNN (R&D 브랜치)
├── 📂 web/
│   ├── app.py             # Streamlit 메인
│   └── pages/
│       ├── 01_ranking.py  # 후보 순위표
│       ├── 02_viewer.py   # 3D 구조 뷰어
│       ├── 03_admet.py    # ADMET 레이더 차트
│       └── 04_llm.py      # LLM RAG 기전 설명
├── 📂 results/
│   ├── top_candidates.csv
│   └── results_report.pdf
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 데이터 소스

| 데이터베이스 | 용도 | API |
|:--|:--|:--|
| [ChEMBL 34](https://www.ebi.ac.uk/chembl/) | FDA 승인 약물 + 생체활성 데이터 | REST |
| [UniProt](https://www.uniprot.org) | 단백질 서열 및 어노테이션 | REST |
| [RCSB PDB](https://www.rcsb.org) | 실험적 단백질 3D 구조 | REST |
| [Open Targets](https://www.opentargets.org) | 표적-질환 연관성 점수 | GraphQL |
| [DrugBank](https://go.drugbank.com) | 약물 기전 및 상호작용 | XML (무료 등록) |
| [PMC Open Access](https://www.ncbi.nlm.nih.gov/pmc/) | RAG용 논문 | Entrez API |

## 기여 방법

```bash
git checkout -b feature/your-feature-name
git commit -m "feat: 기능 설명"
git push origin feature/your-feature-name
```

| 유형 | 브랜치 패턴 |
|:--|:--|
| 기능 추가 | `feature/...` |
| 버그 수정 | `fix/...` |
| R&D 실험 | `research/...` |

## 면책 조항 · 라이선스

본 플랫폼의 결과는 **가설 생성 도구**이며 실험적 검증의 대체재가 아닙니다. 모든 in silico 히트는 반드시 단계적 실험 검증(binding assay → 세포 실험 → 동물 실험)을 거쳐야 합니다.

[MIT License](LICENSE) · 오픈사이언스 가속화를 위해 공개

---

# English

## Overview

**RareTarget Discovery** is a fully open-source AI pipeline for identifying drug repurposing candidates targeting Neuromuscular Autoimmune Disease (NAD) — a chronic rare disease in which autoantibodies attack key receptor proteins at the neuromuscular junction (NMJ), causing progressive muscle weakness. Approximately 10–15% of patients remain refractory to all currently approved therapies.

> ⚠️ This platform is a **pure in silico research tool** and must not be used for clinical decision-making or diagnosis.

### Why Drug Repurposing?

| | De Novo Development | Drug Repurposing |
|:--|:--|:--|
| ⏱ Timeline | 10–15 years | **2–5 years** |
| 💰 Cost | $1B–2.5B+ | **$50M–300M** |
| 🛡 Safety data | Unknown | **Existing clinical data** |
| 📋 IND filing | Full GLP toxicology required | **Prior safety data leveraged** |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   RareTarget Pipeline                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📡 UniProt API ──┐                                     │
│  💊 ChEMBL API  ──┼──→  Data Collection & Preprocessing │
│  🏛 DrugBank    ──┘       (FASTA + SMILES ~2,000 cpds)  │
│                                   │                     │
│            ┌──────────────────────┤                     │
│            ▼                      ▼                     │
│  🧬 Structure Prediction     💊 Ligand Preparation      │
│  ESMFold / AlphaFold2         RDKit + Meeko             │
│            │                      │                     │
│            └──────────┬───────────┘                     │
│                       ▼                                 │
│            ⚙️  AutoDock Vina Docking                    │
│               (6,000+ batch docking runs)               │
│                       │                                 │
│          ┌────────────┼────────────┐                    │
│          ▼            ▼            ▼                    │
│    🤖 Activity      📊 MM-GBSA   🧪 ADMET               │
│    Prediction       Rescoring    Filtering              │
│    DeepPurpose/EGNN                                     │
│          │            │            │                    │
│          └────────────┼────────────┘                    │
│                       ▼                                 │
│          🖥️  Streamlit Dashboard                        │
│          3D Viewer · ADMET Chart · LLM RAG              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## System Requirements & Installation

### Hardware

| Component | Minimum | Recommended |
|:--|:--|:--|
| 🎮 GPU | NVIDIA 8GB VRAM | RTX 3090/4090 24GB |
| 🧠 RAM | 32 GB | 64 GB |
| 💾 Storage | 50 GB SSD | 200 GB NVMe |
| 🐧 OS | Ubuntu 20.04 LTS | Ubuntu 22.04 LTS |

> 💡 If VRAM < 8GB, run structure prediction on [ColabFold](https://colab.research.google.com/github/sokrypton/ColabFold) (free Colab GPU) and download only the `.pdb` outputs locally.

### Docker (Recommended)

```bash
git clone https://github.com/your-org/raretarget-discovery.git
cd raretarget-discovery
docker compose up --build
```

### Local Installation

```bash
conda create -n raretarget python=3.10 && conda activate raretarget
conda install -c conda-forge rdkit
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cu118
pip install torch-geometric torch-scatter torch-sparse
pip install -r requirements.txt

# For LLM RAG
curl -fsSL https://ollama.com/install.sh | sh && ollama pull llama3.2
```

## Running the Pipeline

```bash
python scripts/fetch_targets.py        # 🧬 Fetch protein sequences (UniProt)
python scripts/fetch_drugs.py          # 💊 Fetch FDA-approved drugs (ChEMBL)
python scripts/predict_structures.py   # 🔬 3D structure prediction (ESMFold)
python scripts/run_docking.py          # ⚙️  Batch docking (AutoDock Vina)
python scripts/predict_activity.py     # 🤖 AI activity prediction (DeepPurpose)
python scripts/run_admet.py            # 🧪 ADMET filtering
streamlit run web/app.py               # 🖥️  Launch dashboard → localhost:8501

# Pipeline validation with positive control
python scripts/validate_pipeline.py --control positive_ctrl
```

## Key Parameters

**Docking Thresholds (AutoDock Vina)**

| Binding Affinity | Verdict |
|:--|:--|
| `< −8.0 kcal/mol` | ✅ Hit — top candidate |
| `−6.0 ~ −8.0 kcal/mol` | 🔍 Review required |
| `> −6.0 kcal/mol` | ❌ Discard |

> Top 100 candidates are re-scored with MM-GBSA (AmberTools, free) to reduce false positives.

**ADMET Filters**

| Parameter | Threshold | Rationale |
|:--|:--|:--|
| BBB permeability | logBB < −1 preferred | Peripheral NMJ target — minimize CNS exposure |
| hERG toxicity | IC50 > 10 μM | High cardiac comorbidity burden |
| DILI | Predicted negative | Long-term co-administration considered |
| PAINS | No patterns | Prevents false-positive docking artifacts |

## Project Structure

```
raretarget-discovery/
├── 📂 data/
│   ├── raw/               # Raw API data
│   ├── processed/         # Processed SMILES, FASTA
│   ├── structures/        # .pdb, .pdbqt files
│   └── discovery.db       # Integrated SQLite DB
├── 📂 scripts/            # Pipeline scripts
├── 📂 models/egnn/        # Custom EGNN (R&D branch)
├── 📂 web/
│   ├── app.py             # Streamlit main app
│   └── pages/
│       ├── 01_ranking.py  # Candidate ranking table
│       ├── 02_viewer.py   # 3D docking pose viewer
│       ├── 03_admet.py    # ADMET radar chart
│       └── 04_llm.py      # LLM RAG mechanism explanation
├── 📂 results/
│   ├── top_candidates.csv
│   └── results_report.pdf
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Data Sources

| Database | Purpose | API |
|:--|:--|:--|
| [ChEMBL 34](https://www.ebi.ac.uk/chembl/) | FDA-approved drugs + bioactivity data | REST |
| [UniProt](https://www.uniprot.org) | Protein sequences & annotations | REST |
| [RCSB PDB](https://www.rcsb.org) | Experimental 3D protein structures | REST |
| [Open Targets](https://www.opentargets.org) | Target–disease association scores | GraphQL |
| [DrugBank](https://go.drugbank.com) | Drug mechanisms & interactions | XML (free registration) |
| [PMC Open Access](https://www.ncbi.nlm.nih.gov/pmc/) | Literature for RAG | Entrez API |

## Contributing

```bash
git checkout -b feature/your-feature-name
git commit -m "feat: describe your change"
git push origin feature/your-feature-name
```

| Type | Branch Pattern |
|:--|:--|
| New feature | `feature/...` |
| Bug fix | `fix/...` |
| R&D experiment | `research/...` |

## Disclaimer · License

Results produced by this platform are **hypothesis-generation outputs** and are not substitutes for experimental validation. All in silico hits must undergo stepwise wet-lab verification (binding assay → cell-based assay → animal model) before any conclusions can be drawn.

[MIT License](LICENSE) · Released to accelerate open science

---

# 日本語

## 概要

**RareTarget Discovery** は、神経筋自己免疫希少疾患（Neuromuscular Autoimmune Disease, NAD）を対象としたドラッグリパーパシング（Drug Repurposing）候補を探索する、完全オープンソースの AI パイプラインです。

対象疾患は、自己抗体が神経筋接合部（NMJ）の重要な受容体タンパク質を攻撃し、筋力低下を引き起こす慢性希少疾患であり、全患者の約 10〜15% が現在承認された治療薬に反応しない **難治性（Refractory）** の状態にあります。

> ⚠️ 本プラットフォームは **純粋な in silico 研究ツール** です。臨床的判断や診断には使用できません。

### 新薬開発 vs ドラッグリパーパシング

| 項目 | 新薬開発 | ドラッグリパーパシング |
|:--|:--|:--|
| ⏱ 開発期間 | 10〜15年 | **2〜5年** |
| 💰 コスト | $1B〜2.5B以上 | **$50M〜300M** |
| 🛡 安全性データ | 完全に未知 | **既存の臨床データあり** |
| 📋 IND申請 | 新規 GLP 毒性試験が必要 | **既存毒性データを活用可能** |

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│                   RareTarget Pipeline                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📡 UniProt API ──┐                                     │
│  💊 ChEMBL API  ──┼──→  データ収集 & 前処理              │
│  🏛 DrugBank    ──┘    （FASTA + SMILES 約2,000化合物）  │
│                                   │                     │
│            ┌──────────────────────┤                     │
│            ▼                      ▼                     │
│  🧬 タンパク質構造予測        💊 リガンド準備             │
│  ESMFold / AlphaFold2         RDKit + Meeko             │
│            │                      │                     │
│            └──────────┬───────────┘                     │
│                       ▼                                 │
│            ⚙️  AutoDock Vina ドッキング                  │
│               （6,000回以上のバッチドッキング）           │
│                       │                                 │
│          ┌────────────┼────────────┐                    │
│          ▼            ▼            ▼                    │
│    🤖 AI活性予測    📊 MM-GBSA   🧪 ADMET               │
│    DeepPurpose/EGNN  再スコアリング  フィルタリング       │
│          │            │            │                    │
│          └────────────┼────────────┘                    │
│                       ▼                                 │
│          🖥️  Streamlit ダッシュボード                    │
│          3D ビューワー · ADMET チャート · LLM RAG        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## システム要件 & インストール

### ハードウェア

| 項目 | 最小要件 | 推奨要件 |
|:--|:--|:--|
| 🎮 GPU | NVIDIA 8GB VRAM | RTX 3090/4090 24GB |
| 🧠 RAM | 32 GB | 64 GB |
| 💾 ストレージ | 50 GB SSD | 200 GB NVMe |
| 🐧 OS | Ubuntu 20.04 LTS | Ubuntu 22.04 LTS |

> 💡 VRAM が 8GB 未満の場合は、[ColabFold](https://colab.research.google.com/github/sokrypton/ColabFold)（Colab 無料 GPU）で構造予測を行い、`.pdb` ファイルのみローカルに保存するハイブリッド戦略を推奨します。

### Docker（推奨）

```bash
git clone https://github.com/your-org/raretarget-discovery.git
cd raretarget-discovery
docker compose up --build
```

### ローカルインストール

```bash
conda create -n raretarget python=3.10 && conda activate raretarget
conda install -c conda-forge rdkit
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cu118
pip install torch-geometric torch-scatter torch-sparse
pip install -r requirements.txt

# LLM RAG を使用する場合
curl -fsSL https://ollama.com/install.sh | sh && ollama pull llama3.2
```

## パイプライン実行

```bash
python scripts/fetch_targets.py        # 🧬 タンパク質配列取得 (UniProt)
python scripts/fetch_drugs.py          # 💊 FDA承認薬取得 (ChEMBL)
python scripts/predict_structures.py   # 🔬 3D構造予測 (ESMFold)
python scripts/run_docking.py          # ⚙️  バッチドッキング (AutoDock Vina)
python scripts/predict_activity.py     # 🤖 AI活性予測 (DeepPurpose)
python scripts/run_admet.py            # 🧪 ADMETフィルタリング
streamlit run web/app.py               # 🖥️  ダッシュボード起動 → localhost:8501

# パイプライン検証（陽性コントロール）
python scripts/validate_pipeline.py --control positive_ctrl
```

## 主要パラメータ

**ドッキング基準（AutoDock Vina）**

| 結合親和性 | 判定 |
|:--|:--|
| `< −8.0 kcal/mol` | ✅ ヒット — 上位候補 |
| `−6.0 〜 −8.0 kcal/mol` | 🔍 要検討 |
| `> −6.0 kcal/mol` | ❌ 除外 |

> 上位100位の候補は MM-GBSA 再スコアリング（AmberTools、無料）により false positive をさらに除去します。

**ADMET フィルター**

| 項目 | 基準 | 備考 |
|:--|:--|:--|
| BBB 透過性 | logBB < −1 を推奨 | 末梢 NMJ 標的、CNS 副作用最小化 |
| hERG 毒性 | IC50 > 10 μM | 心臓合併症を持つ患者が多い |
| DILI | 予測陰性 | 長期併用投与を考慮 |
| PAINS | パターンなし | false-positive ドッキングを防止 |

## プロジェクト構成

```
raretarget-discovery/
├── 📂 data/
│   ├── raw/               # API 生データ
│   ├── processed/         # 前処理済み SMILES, FASTA
│   ├── structures/        # .pdb, .pdbqt ファイル
│   └── discovery.db       # SQLite 統合 DB
├── 📂 scripts/            # パイプラインスクリプト
├── 📂 models/egnn/        # カスタム EGNN（R&D ブランチ）
├── 📂 web/
│   ├── app.py             # Streamlit メインアプリ
│   └── pages/
│       ├── 01_ranking.py  # 候補ランキング表
│       ├── 02_viewer.py   # 3D 構造ビューワー
│       ├── 03_admet.py    # ADMET レーダーチャート
│       └── 04_llm.py      # LLM RAG 機序説明
├── 📂 results/
│   ├── top_candidates.csv
│   └── results_report.pdf
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## データソース

| データベース | 用途 | API |
|:--|:--|:--|
| [ChEMBL 34](https://www.ebi.ac.uk/chembl/) | FDA 承認薬 + 生体活性データ | REST |
| [UniProt](https://www.uniprot.org) | タンパク質配列 & アノテーション | REST |
| [RCSB PDB](https://www.rcsb.org) | 実験的 3D タンパク質構造 | REST |
| [Open Targets](https://www.opentargets.org) | 標的-疾患関連スコア | GraphQL |
| [DrugBank](https://go.drugbank.com) | 薬物機序 & 相互作用 | XML（無料登録） |
| [PMC Open Access](https://www.ncbi.nlm.nih.gov/pmc/) | RAG 用論文データ | Entrez API |

## コントリビューション

```bash
git checkout -b feature/your-feature-name
git commit -m "feat: 変更内容の説明"
git push origin feature/your-feature-name
```

| 種類 | ブランチパターン |
|:--|:--|
| 機能追加 | `feature/...` |
| バグ修正 | `fix/...` |
| R&D 実験 | `research/...` |

## 免責事項 · ライセンス

本プラットフォームが出力する結果は **仮説生成ツール** であり、実験的検証の代替ではありません。すべての in silico ヒットは、結合アッセイ → 細胞実験 → 動物実験という段階的な湿式検証を経る必要があります。

[MIT License](LICENSE) · オープンサイエンスの加速のために公開

---

<div align="center">

**RareTarget Discovery** · Open Science · Zero Cloud Cost

*한국어 · English · 日本語*

</div>

---

# 🚀 AlphaFold Drug Platform - Quick Start

## 📦 빠른 시작 (Quick Start)

### 1. 환경 설정

```bash
# 1) 저장소 클론
git clone https://github.com/danjjak-ai/alphafold-drug-platform.git
cd alphafold-drug-platform

# 2) uv로 가상환경 생성 및 패키지 설치
uv venv .venv
uv pip install -r requirements.txt
```

### 2. AutoDock Vina 설치 (OS별)

> **중요**: AutoDock Vina 바이너리는 OS에 따라 별도로 준비해야 합니다.

| OS | 바이너리 위치 | 다운로드 |
|---|---|---|
| **Windows** | `scripts/vina.exe` | ✅ Git에 포함 (별도 설치 불필요) |
| **Linux** | `vina_bin/linux/vina` | ⬇️아래 안내 참고 |
| **macOS** | `vina_bin/mac/vina` | ⬇️아래 안내 참고 |

#### Linux 설치
```bash
wget https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_linux_x86_64 -O vina_bin/linux/vina
chmod +x vina_bin/linux/vina
```

#### macOS 설치
```bash
curl -L https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_mac_x86_64 -o vina_bin/mac/vina
chmod +x vina_bin/mac/vina
```

---

## 🖥️ 서비스 기동

### 데이터 파이프라인 실행 (최초 1회)

**Windows:** `run_pipeline.bat`  
**Linux / macOS:** `chmod +x run_pipeline.sh && ./run_pipeline.sh`

### 대시보드 기동

**Windows:** `start_dashboard.bat`  
**Linux / macOS:** `chmod +x start_dashboard.sh && ./start_dashboard.sh`

접속 URL: **http://localhost:8501**
