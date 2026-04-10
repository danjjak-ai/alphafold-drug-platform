<div align="center">

<img src="https://github.com/danjjak-ai/alphafold-drug-platform/blob/master/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202026-03-20%20151436.png" alt="Discovery Core Banner" width="800"/>

# 🧬 Discovery Core (RareTarget Discovery)

### AI-Powered Drug Repurposing Platform for Rare Neuromuscular Disease
**AI-driven screening and data pipeline for Myasthenia Gravis (MG) drug discovery.**

**[한국어](#-한국어) · [English](#-english) · [日本語](#-日本語)**

---

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![PyTorch 2.1+](https://img.shields.io/badge/PyTorch-2.1+-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org)
[![RDKit](https://img.shields.io/badge/RDKit-2023.09+-1D9E75?style=flat-square)](https://www.rdkit.org)
[![AutoDock Vina](https://img.shields.io/badge/AutoDock_Vina-1.2.5-FF6B35?style=flat-square)](https://vina.scripps.edu)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)

</div>

---

# 🇰🇷 한국어

## 📖 프로젝트 배경 (Research)
**Discovery Core**는 희귀 신경근 자가면역 질환인 **중증근무력증(Myasthenia Gravis, MG)**의 치료제 개발을 가속화하기 위해 제약 지식과 IT 기술을 결합한 플랫폼입니다.

### 1. 질환 개요
중증근무력증은 신경근 접합부(NMJ)에서 자가항체에 의해 신호 전달이 차단되어 발생하는 질환입니다. 안검하수, 사지 근력 약화 등을 초래하며, 약 10~15%의 환자는 기존 치료제에 반응하지 않는 **치료 저항성(Refractory MG)**을 보입니다. 본 프로젝트는 이러한 미충족 의료 수요를 해결하기 위해 이미 안전성이 검증된 FDA 승인 약물 중에서 새로운 기전을 찾는 **약물 재창출(Drug Repurposing)** 전략을 채택합니다.

### 2. 핵심 생물학적 표적 (Molecular Targets)
- **CHRNA1 (AChR α1)**: 자가항체의 주요 타겟으로, 수용체 분해를 막고 이온 채널 개방을 안정화하는 약물을 탐색합니다.
- **MuSK (Muscle-Specific Kinase)**: NMJ 형성에 필수적인 효소로, MuSK-양성 MG 환자를 위해 키나제 활성화를 유도하는 조절제를 찾습니다.
- **LRP4**: MuSK와 상호작용하여 신호를 복합체화하는 수용체입니다.

---

## 🚀 주요 기능 및 시스템 아키텍처 (Technical)
본 플랫폼은 데이터 수집부터 AI 모델링, 시각화까지 전 과정을 자동화한 엔드투엔드 파이프라인을 제공합니다.

### 🛠️ 기술 스택
- **Cheminformatics**: RDKit (분자 전처리), Meeko (PDBQT 변환), ChEMBL API (데이터 소스)
- **AI/ML 모델링**: PyTorch, PyTorch Geometric, DeepChem (GCN, EGNN 기반 활성 예측)
- **Simulation**: AutoDock Vina 1.2.5 (Batch 도킹), MDAnalysis (`미구현`)
- **Frontend/UI**: Streamlit, Tailwind CSS (UI 디자인), 3Dmol.js (3D 분자 렌더링)
- **Infrastructure**: **uv** (Package Manager), Docker, Google Cloud Run

### 💻 시스템 요구사항
| 구분 | 최소 사양 | 권장 사양 |
|---|---|---|
| **GPU** | NVIDIA GPU 8GB VRAM | NVIDIA RTX 3090/4090 24GB |
| **RAM** | 32 GB | 64 GB 이상 |
| **OS** | Windows 10/11 | Ubuntu 22.04 LTS |

---

## 🧬 전체 데이터 파이프라인 (Execution)
일관된 결과를 위해 다음 단계로 스크리닝을 진행합니다 (`run_pipeline.bat` 사용 시 자동화):

1.  **DB 초기화**: SQLite DB(`mg_discovery.db`) 스키마 생성.
2.  **타겟 및 약물 수집**: UniProt 및 ChEMBL API를 통해 질환 관련 데이터 수집.
3.  **구조 예측 (`predict_structures.py`)**: ESMFold 및 AlphaFold2를 활용한 3D 단백질 구조 생성.
4.  **전처리**: 리간드(LIG) 및 수용체(REC)의 .pdbqt 변환.
5.  **가상 스크리닝 (`run_docking.py`)**: AutoDock Vina를 이용한 대규모 병렬 도킹.
6.  **AI 활성 예측**: 도킹 결과를 기반으로 GCN 모델을 통한 복합체 활성 예측.
7.  **대시보드 분석**: Streamlit 기반의 인터랙티브 결과 웹 앱 실행.

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

---

# 🇺🇸 English

## 📖 Background (Research)
**Discovery Core** is an integrated platform combining pharmaceutical knowledge and AI technology to accelerate the development of treatments for **Myasthenia Gravis (MG)**, a rare neuromuscular autoimmune disease.

### 1. Disease Overview
MG is caused by autoantibodies blocking signal transmission at the Neuromuscular Junction (NMJ). It leads to muscle weakness, and approximately 10-15% of patients show **Refractory MG**, failing to respond to conventional treatments. This project adopts a **Drug Repurposing** strategy to find novel mechanisms among safety-proven FDA-approved drugs.

### 2. Key Biological Targets
- **CHRNA1 (AChR α1)**: Primary target of autoantibodies; searching for compounds that stabilize ion channels and prevent receptor degradation.
- **MuSK (Muscle-Specific Kinase)**: Essential for NMJ formation; searching for positive allosteric modulators for MuSK-positive MG.
- **LRP4**: A receptor that interacts with MuSK to complex signals for NMJ maintenance.

---

## 🚀 Key Features & Architecture (Technical)
An end-to-end automated pipeline from data collection to AI modeling and visualization.

### 🛠️ Tech Stack
- **Cheminformatics**: RDKit (Preprocessing), Meeko (PDBQT), ChEMBL API.
- **AI/ML Modeling**: PyTorch, PyG, DeepChem (GCN, EGNN-based prediction).
- **Simulation**: AutoDock Vina 1.2.5 (Batch Docking), MDAnalysis (`Unimplemented`).
- **Dashboard**: Streamlit, Tailwind CSS, 3Dmol.js (3D visualization).
- **Infrastructure**: **uv** (Package Manager), Docker, Google Cloud Run.

### 💻 System Requirements
| Component | Minimum | Recommended |
|---|---|---|
| **GPU** | 8GB VRAM | 24GB VRAM (RTX 4090) |
| **RAM** | 32 GB | 64 GB+ |
| **OS** | Windows 10/11 | Ubuntu 22.04 LTS |

---

## 🧬 Automated Data Pipeline (Execution)
Automated screening steps (Execute via `run_pipeline.bat` on Windows):
1. **Init DB**: Create SQLite schema (`mg_discovery.db`).
2. **Fetch Data**: Collect target and drug data via UniProt and ChEMBL.
3. **Predict Structure**: Generate 3D models using ESMFold or AlphaFold2.
4. **Prepare Structures**: Convert ligands and receptors to .pdbqt format.
5. **Virtual Screening**: High-throughput docking with AutoDock Vina.
6. **Activity Prediction**: Infer binding activity using GCN models.
7. **Analytics**: Launch interactive dashboard via Streamlit.

---

## 🗺️ Implementation Roadmap (Status)
- [x] **Phase 1**: Data Pipeline (Done)
- [x] **Phase 2**: Virtual Screening (Done)
- [x] **Phase 3**: AI Activity Prediction (Done - GCN/RF Models)
- [x] **Phase 4**: LLM RAG-powered Mechanistic Insights (Done - Ollama Llama 3.2)
- [x] **Phase 5**: MM-GBSA Precision Rescoring (Done - AmberTools Integration)
- [x] **Phase 6**: Automated Analytical Reporting (Done - Markdown Report Generator)

---

# 🇯🇵 日本語

## 📖 プロジェクト背景 (Research)
**Discovery Core** は、希少神経筋疾患である **重症筋無力症 (Myasthenia Gravis, MG)** の治療薬開発を加速させるため、製薬知識と AI 技術を統合したプラットフォームです。

### 1. 疾患の概要
重症筋無力症は、神経筋接合部 (NMJ) において自己抗体が信号伝達を遮断することで発生する疾患です。筋力低下を引き起こし、患者の約 10〜15% は既存の治療法に反応しない **難治性 MG (Refractory MG)** を呈します。本プロジェクトは、安全性が証明済みの FDA 承認薬の中から新たな機序を探索する **ドラッグリパーパシング (既存薬再開発)** 戦略を採用しています。

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

## 🗺️ ロードマップと進捗状況 (Status)
- [x] **Phase 1**: データパイプライン構築 (完了)
- [x] **Phase 2**: 仮想スクリーニングシステム (完了)
- [x] **Phase 3**: AI 活性予測モデル (完了 - GCN/RF モデル)
- [x] **Phase 4**: LLM RAG による機序説明生成 (完了 - Ollama Llama 3.2 搭載)
- [x] **Phase 5**: MM-GBSA 精密再スコアリング (完了 - AmberTools 連携済み)
- [x] **Phase 6**: 自動分析レポート生成機能 (完了 - Markdown レポート生成)

---

## 📂 Project Structure
```
alphafold-drug-platform/
├── 📂 data/               # Raw/Processed data, structures, and SQLite DB
├── 📂 scripts/            # Pipeline, preprocessing, and ML training scripts
├── 📂 web/                # Streamlit dashboard & React components
├── 📂 results/            # Simulation outputs and CSV reports
├── 📂 models/             # Pre-trained ML model checkpoints
└── requirements.txt       # Project dependencies
```

## 📜 License
Released under the [MIT License](LICENSE).
<br>
*Copyright (c) 2026 Danjjak-AI Team. Accelerating open science for rare diseases.*

</div>
