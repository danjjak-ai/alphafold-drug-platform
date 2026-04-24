<div align="center">

<img src="https://github.com/danjjak-ai/alphafold-drug-platform/blob/master/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202026-03-20%20151436.png" alt="Discovery Core Banner" width="800"/>

# 🧬 Discovery Core (RareTarget Discovery)

### AI-Powered Dynamic Drug Repurposing Platform
**Any disease input, automatic target/drug fetching, and AI-driven screening pipeline.**

**[한국어](#-한국어) · [English](#-english) · [日本語](#-日本語)**

---

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![PyTorch 2.1+](https://img.shields.io/badge/PyTorch-2.1+-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org)
[![RDKit](https://img.shields.io/badge/RDKit-2023.09+-1D9E75?style=flat-square)](https://www.rdkit.org)
[![AutoDock Vina](https://img.shields.io/badge/AutoDock_Vina-1.2.5-FF6B35?style=flat-square)](https://vina.scripps.edu)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Google Colab](https://img.shields.io/badge/Google_Colab-F9AB00?style=flat-square&logo=googlecolab&logoColor=white)](https://colab.research.google.com)

</div>

---

# 🇰🇷 한국어

## 📖 프로젝트 배경 (Research)
**Discovery Core**는 특정 질환에 국한되지 않고, 사용자가 입력한 **어떠한 질환**에 대해서도 관련 타겟과 약물을 자동으로 수집하여 분석하는 범용 AI 약물 재창출 플랫폼입니다.

### 1. 질환 개요
중증근무력증은 신경근 접합부(NMJ)에서 자가항체에 의해 신호 전달이 차단되어 발생하는 질환입니다. 안검하수, 사지 근력 약화 등을 초래하며, 약 10~15%의 환자는 기존 치료제에 반응하지 않는 **치료 저항성(Refractory MG)**을 보입니다. 본 프로젝트는 이러한 미충족 의료 수요를 해결하기 위해 이미 안전성이 검증된 FDA 승인 약물 중에서 새로운 기전을 찾는 **약물 재창출(Drug Repurposing)** 전략을 채택합니다.

### 2. 핵심 생물학적 표적 (Molecular Targets)
- **CHRNA1 (AChR α1)**: 자가항체의 주요 타겟으로, 수용체 분해를 막고 이온 채널 개방을 안정화하는 약물을 탐색합니다.
- **MuSK (Muscle-Specific Kinase)**: NMJ 형성에 필수적인 효소로, MuSK-양성 MG 환자를 위해 키나제 활성화를 유도하는 조절제를 찾습니다.
- **LRP4**: MuSK와 상호작용하여 신호를 복합체화하는 수용체입니다.

---

## 🚀 주요 기능 및 시스템 아키텍처 (Technical)
본 플랫폼은 데이터 수집부터 AI 모델링, 시각화까지 전 과정을 자동화한 엔드투엔드 파이프라인을 제공합니다. 특히 **로컬 리소스의 한계를 극복하기 위해 Google Colab과의 하이브리드 연동**을 지원합니다.

### 🛠️ 기술 스택
- **Cheminformatics**: RDKit (분자 전처리), Meeko (PDBQT 변환), ChEMBL API (데이터 소스)
- **AI/ML 모델링**: PyTorch, PyTorch Geometric, DeepChem (GCN, EGNN 기반 활성 예측)
- **Simulation**: AutoDock Vina 1.2.5 (Batch 도킹), AmberTools (MM-GBSA)
- **Frontend/UI**: Streamlit, Tailwind CSS (UI 디자인), 3Dmol.js (3D 분자 렌더링)
- **Infrastructure**: **Google Colab (Backend)**, **uv** (Local Package Manager), Ollama (Local RAG)

### 💻 시스템 요구사항
| 구분 | 로컬 단독 실행 시 | Colab 하이브리드 실행 시 (권장) |
|---|---|---|
| **GPU** | NVIDIA 8GB VRAM 이상 | **불필요 (Colab GPU 활용)** |
| **RAM** | 32 GB 이상 | 16 GB 이상 |
| **OS** | Windows 10/11, Ubuntu | Windows 10/11, Ubuntu |

---

## ☁️ Google Colab 클라우드 파이프라인
고사양 GPU가 없거나 대규모 병렬 도킹이 필요한 경우 Google Colab을 통해 백엔드 연산을 수행할 수 있습니다.

1.  **Colab 실행**: `Discovery_Core_Colab_Pipeline.ipynb` 파일을 Google Colab에서 엽니다.
2.  **데이터 처리**: 노트북의 셀을 순차적으로 실행하여 데이터 수집, 도킹, AI 학습을 진행합니다.
3.  **결과 다운로드**: 모든 과정이 끝나면 `discovery_results.zip` 파일이 자동으로 다운로드됩니다.
4.  **로컬 임포트**: 다운로드된 압축 파일을 프로젝트 루트 폴더에 넣고 `import_results.bat`를 실행합니다.
5.  **대시보드 확인**: `start_dashboard.bat`를 실행하여 결과를 확인합니다.

---

## 🧬 전체 데이터 파이프라인 (Execution)
로컬에서 전체 과정을 직접 실행하려면 다음 단계를 따릅니다 (`run_pipeline.bat` 사용 시 자동화):

1.  **DB 초기화**: SQLite DB(`mg_discovery.db`) 스키마 생성.
2.  **질환 기반 데이터 수집**: 사용자 입력 질환명(예: Alzheimer, MG 등)을 바탕으로 UniProt 및 ChEMBL API를 통해 관련 타겟 및 약물 자동 수집.
3.  **구조 예측**: 수집된 타겟의 PDB 정보를 확인하고, ESMFold 및 AlphaFold2를 활용하여 3D 구조 자동 준비.
4.  **전처리**: 리간드(LIG) 및 수용체(REC)의 .pdbqt 변환.
5.  **가상 스크리닝**: AutoDock Vina를 이용한 대규모 병렬 도킹.
6.  **AI 활성 예측**: GCN 모델을 통한 복합체 활성 예측 및 재채점.
7.  **MM-GBSA 보정**: AmberTools를 이용한 결합 에너지 정밀 계산.
8.  **대시보드 분석**: Streamlit 기반의 인터랙티브 결과 웹 앱 실행.

---

## 🗺️ 로드맵 및 구현 상태 (Status)

| Phase | 마일스톤 | 현 상태 | 비고 |
|---|---|---|---|
| **Phase 1** | 데이터 파이프라인 구축 | **완료** | ChEMBL/UniProt 연동 및 DB화 |
| **Phase 2** | 가상 스크리닝 시스템 | **완료** | Vina Batch 도킹 및 3D 뷰어 |
| **Phase 3** | AI 활성 예측 모델 | **완료** | GCN/RF 모델 기반 활성 추론 |
| **Phase 4** | LLM RAG 기반 기전 설명 | **완료** | Ollama(Llama 3.2) 기반 로컬 분석 엔진 |
| **Phase 5** | MM-GBSA 정밀 재채점 | **완료** | AmberTools 연동 시뮬레이션 및 스코어 보정 |
| **Phase 6** | 최종 결과 보고서 자동화 | **완료** | Markdown/PDF 분석 리포트 생성 기능 |
| **Phase 7** | **Colab 클라우드 연동** | **완료** | 고성능 백엔드 이관 및 데이터 임포터 구축 |

---

# 🇺🇸 English

## 📖 Background (Research)
**Discovery Core** is a universal AI drug repurposing platform that automatically collects and analyzes relevant targets and drugs for **any disease** entered by the user, moving beyond specific disease constraints.

### 1. Disease Overview
MG is caused by autoantibodies blocking signal transmission at the Neuromuscular Junction (NMJ). It leads to muscle weakness, and approximately 10-15% of patients show **Refractory MG**, failing to respond to conventional treatments. This project adopts a **Drug Repurposing** strategy to find novel mechanisms among safety-proven FDA-approved drugs.

### 2. Key Biological Targets
- **CHRNA1 (AChR α1)**: Primary target of autoantibodies; searching for compounds that stabilize ion channels and prevent receptor degradation.
- **MuSK (Muscle-Specific Kinase)**: Essential for NMJ formation; searching for positive allosteric modulators for MuSK-positive MG.
- **LRP4**: A receptor that interacts with MuSK to complex signals for NMJ maintenance.

---

## 🚀 Key Features & Architecture (Technical)
An end-to-end automated pipeline from data collection to AI modeling and visualization. Now supporting **Hybrid Cloud integration with Google Colab** to overcome local resource constraints.

### 🛠️ Tech Stack
- **Cheminformatics**: RDKit, Meeko, ChEMBL API.
- **AI/ML Modeling**: PyTorch, PyG, DeepChem (GCN, EGNN-based prediction).
- **Simulation**: AutoDock Vina 1.2.5, AmberTools (MM-GBSA).
- **Frontend/UI**: Streamlit, Tailwind CSS, 3Dmol.js (3D visualization).
- **Infrastructure**: **Google Colab (Backend)**, **uv** (Local Manager), Ollama (Local RAG).

### 💻 System Requirements
| Component | Local Standalone | Colab Hybrid (Recommended) |
|---|---|---|
| **GPU** | 8GB+ VRAM | **Optional (Uses Colab GPU)** |
| **RAM** | 32 GB | 16 GB |
| **OS** | Windows 10/11, Ubuntu | Windows 10/11, Ubuntu |

---

## ☁️ Google Colab Cloud Pipeline
If you lack a high-end GPU or need large-scale docking, use the cloud-based backend.

1.  **Open Notebook**: Open `Discovery_Core_Colab_Pipeline.ipynb` in Google Colab.
2.  **Process Data**: Run all cells to perform data collection, docking, and AI training.
3.  **Download Results**: After completion, `discovery_results.zip` will be downloaded automatically.
4.  **Import Locally**: Place the zip file in the project root and run `import_results.bat`.
5.  **Visualize**: Run `start_dashboard.bat` to explore the results in the dashboard.

---

## 🧬 Automated Data Pipeline (Execution)
Automated screening steps (Execute via `run_pipeline.bat` on Windows):
1. **Init DB**: Create SQLite schema (`mg_discovery.db`).
2. **Fetch Data**: Collect target and drug data via UniProt and ChEMBL.
3. **Predict Structure**: Generate 3D models using ESMFold or AlphaFold2.
4. **Prepare Structures**: Convert ligands and receptors to .pdbqt format.
5. **Virtual Screening**: High-throughput docking with AutoDock Vina.
6. **Activity Prediction**: binding activity prediction & MM-GBSA rescoring.
7. **Analytics**: Launch interactive dashboard via Streamlit.

---

## 🗺️ Implementation Roadmap (Status)
- [x] **Phase 1**: Data Pipeline (Done)
- [x] **Phase 2**: Virtual Screening (Done)
- [x] **Phase 3**: AI Activity Prediction (Done)
- [x] **Phase 4**: LLM RAG-powered Insights (Done)
- [x] **Phase 5**: MM-GBSA Precision Rescoring (Done)
- [x] **Phase 6**: Automated Analytical Reporting (Done)
- [x] **Phase 7**: **Colab Cloud Integration** (Done)

---

# 🇯🇵 日本語

## 📖 プロジェクト背景 (Research)
**Discovery Core** は、希少神経筋疾患である **重症筋無力症 (Myasthenia Gravis, MG)** の治療薬開発を加速させるプラットフォームです.

### 1. 疾患の概要
神経筋接合部 (NMJ) において自己抗体が信号伝達を遮断することで発生する疾患です。筋力低下を引き起こし、患者の約 10〜15% は既存の治療法に反応しない **難治性 MG (Refractory MG)** を呈します。本プロジェクトは、安全性が証明済みの FDA 承認薬の中から新たな機序を探索する **ドラッグリパーパシング (既存薬再開発)** 戦略を採用しています。

### 2. 主要な生物学的標的
- **CHRNA1 (AChR α1)**: 自己抗体の主要な標的。受容体の分解を防ぎ、イオンチャネルの開放を安定化させる化合物を探索します。
- **MuSK (Muscle-Specific Kinase)**: NMJ 形成に不可欠な酵素。MuSK 陽性 MG 患者向けにキナーゼ活性化を誘導する調節因子を探索。
- **LRP4**: MuSK と相互作用し、NMJ 維持のための信号を複合体化する受容体。

---

## 🚀 主な機能とシステムアーキテクチャ (Technical)
データ収集から AI モデリング、可視化までを自動化したエンドツーエンドのパイプラインを提供します。

### 🛠️ 技術スタック
- **ケモインフォマティクス**: RDKit (前処理), Meeko (PDBQT 変換), ChEMBL API (データソース)
- **AI/ML モデリング**: PyTorch, PyG, DeepChem (GCN, EGNN ベースの活性予測)
- **シミュレーション**: AutoDock Vina 1.2.5 (バッチドッキング), MDAnalysis (`未実装`)
- **UI/UX**: Streamlit, Tailwind CSS (UI デザイン), 3Dmol.js (3D 分子レンダリング)
- **インフラ**: **uv** (パッケージマネージャー), Docker, Google Cloud Run

### 💻 システム要件
| 項目 | 最小構成 | 推奨構成 |
|---|---|---|
| **GPU** | NVIDIA 8GB VRAM | NVIDIA 24GB VRAM (RTX 4090) |
| **RAM** | 32 GB | 64 GB 以上 |
| **OS** | Windows 10/11 | Ubuntu 22.04 LTS |

---

## 🧬 データパイプライン (Execution)
以下のステップでスクリーニングを実施します (`run_pipeline.bat` で自動化):
1. **DB 初期化**: SQLite DB (`mg_discovery.db`) の構築。
2. **収集**: UniProt および ChEMBL API を介した標的・化合物データの取得。
3. **予測**: ESMFold または AlphaFold2 を用いた 3D タンパク質構造予測。
4. **準備**: リガンドおよび受容体の .pdbqt 形式への変換。
5. **ドッキング**: AutoDock Vina による大規模並列シミュレーション。
6. **AI 推論**: GCN モデルによる化合物活性のクラス分類と予測。
7. **分析**: Streamlit によるインタラクティブなダミボードの実行。

---

## 🗺️ 進捗状況 (Status)
- [x] **Phase 1-6**: 基本機能の実装 (完了)
- [x] **Phase 7**: **Colab クラウド連携** (完了)

---

## 📂 Project Structure
```
alphafold-drug-platform/
├── 📂 data/               # Raw/Processed data, structures, and SQLite DB
├── 📂 scripts/            # Pipeline, preprocessing, and ML training scripts
├── 📂 web/                # Streamlit dashboard & React components
├── 📂 results/            # Simulation outputs and CSV reports
├── 📂 models/             # Pre-trained ML model checkpoints
├── Discovery_Core_Colab_Pipeline.ipynb  # Colab Pipeline Notebook
├── import_results.bat     # Colab Result Importer (Windows)
└── requirements.txt       # Project dependencies
```

## 📜 License
Released under the [MIT License](LICENSE).
<br>
*Copyright (c) 2026 Danjjak-AI Team. Accelerating open science for rare diseases.*

</div>
