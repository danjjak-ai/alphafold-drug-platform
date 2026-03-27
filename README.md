<div align="center">

<img src="https://github.com/danjjak-ai/alphafold-drug-platform/blob/master/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202026-03-20%20151436.png" alt="Discovery Core Banner" width="800"/>

# 🧬 Discovery Core (RareTarget Discovery)

### AI-Powered Drug Repurposing Platform for Rare Neuromuscular Disease

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

## 📖 개요

**Discovery Core**는 중증근무력증(Myasthenia Gravis)과 같은 희귀 신경근 질환(Neuromuscular Autoimmune Disease, NAD) 치료를 위한 **약물 재창출(Drug Repurposing)** 후보를 발굴하는 AI 통합 플랫폼입니다. 

기존의 10년 이상 걸리는 신약 개발 과정을 효율화하여, 이미 안전성이 검증된 FDA 승인 약물 중에서 새로운 타겟 단백질(CHRNA1, MuSK, LRP4 등)에 결합하는 최적의 후보를 AI가 예측하고 시뮬레이션합니다.

> ⚠️ **본 플랫폼은 순수 In Silico 연구 도구입니다.** 임상적 판단이나 진단 목적으로 사용할 수 없습니다.

## 🚀 주요 기능

- **🧬 단백질 구조 예측**: ESMFold 및 AlphaFold2를 활용한 정밀한 3D 단백질 구조 빔 생성.
- **💊 약물 라이브러리 자동화**: ChEMBL API를 통해 FDA 승인 약물 데이터를 실시간 수집 및 전처리.
- **⚙️ 가상 스크리닝**: AutoDock Vina를 이용한 대규모 병렬 도킹 시뮬레이션.
- **🤖 AI 활성 예측**: EGNN(E(3)-equivariant Graph Neural Networks) 및 DeepPurpose를 통한 약물-표적 활성 예측.
- **🖥️ 인터랙티브 대시보드**: Streamlit과 React 기반의 3D 분자 뷰어, MD 시뮬레이션 결과 분석, LLM RAG 기반 기전 설명.

## 🛠️ 설치 및 환경 설정

본 프로젝트는 최신 파이썬 패키지 매니저인 **uv**를 표준으로 사용합니다.

### 1. 가상환경 구축
```bash
# uv 설치 (이미 있다면 생략)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 가상환경 생성 및 패키지 설치
uv venv .venv
uv pip install -r requirements.txt
```

### 2. AutoDock Vina 바이너리 설정
- **Windows**: `scripts/vina.exe`가 포함되어 있습니다.
- **Linux/macOS**: `vina_bin/` 폴더 내에 해당 OS용 바이너리를 준비하고 실행 권한을 부여하세요.

## 🧬 전체 데이터 파이프라인

일관된 결과를 위해 다음 순서로 스크리닝을 진행합니다 (또는 `run_pipeline.bat` 사용):

1. **DB 초기화**: `python scripts/init_db.py`
2. **타겟 수집 (UniProt)**: `python scripts/fetch_targets.py "Myasthenia Gravis"`
3. **약물 수집 (ChEMBL)**: `python scripts/fetch_drugs.py "Myasthenia Gravis"`
4. **학습 데이터 수집**: `python scripts/fetch_training_data.py`
5. **구조 예측**: `python scripts/predict_structures.py` (AlphaFold 사용 시)
6. **타겟 전처리**: `python scripts/prepare_targets.py`
7. **리간드 전처리**: `python scripts/prepare_ligands.py`
8. **도킹 시뮬레이션**: `python scripts/run_docking.py`
9. **결과 분석**: `python scripts/post_docking_analysis.py`
10. **활성 예측**: `python scripts/predict_activity.py`

## 🖥️ 대시보드 실행

시뮬레이션이 완료되면 다음 명령으로 분석 대시보드를 실행할 수 있습니다.

```bash
# Windows
start_dashboard.bat

# Linux / macOS
chmod +x start_dashboard.sh && ./start_dashboard.sh
```
접속 URL: **http://localhost:8501**

---

# 🇺🇸 English

## 📖 Overview

**Discovery Core** is an AI-integrated platform for identifying **drug repurposing** candidates for rare neuromuscular autoimmune diseases (NAD) such as Myasthenia Gravis. By leveraging deep learning and high-throughput molecular docking, we accelerate the discovery of novel therapeutic uses for existing FDA-approved drugs.

## 🚀 Key Features

*   **Structure Prediction**: Predict high-fidelity 3D protein structures using ESMFold and AlphaFold2.
*   **Automated Library**: Dynamic collection of FDA-approved compounds via ChEMBL API.
*   **Virtual Screening**: Scale-out batch docking simulations with AutoDock Vina.
*   **AI Inference**: Activity prediction using EGNN (Equivariant GNN) and DeepPurpose models.
*   **Interactive UI**: Next-gen dashboard featuring 3D viewers, MD simulation analysis, and LLM-powered biological insights.

## 🛠️ Installation

```bash
# Install dependencies with uv
uv venv .venv
# Activate .venv and install
uv pip install -r requirements.txt
```

## 🧬 Pipeline Workflow

Run the full automated pipeline via `run_pipeline.bat` (Windows) or `./run_pipeline.sh` (Linux). The internal steps involve:
1. DB Initialization -> 2. Target/Drug Fetching -> 3. Structure Preparation -> 4. Batch Docking -> 5. AI Activity Scrambling -> 6. Dashboard Visualization.

---

# 🇯🇵 日本語

## 📖 概要

**Discovery Core** は、重症筋無力症（Myasthenia Gravis）などの希少神経筋疾患の治療を目的とした **ドラッグリパーパシング（既存薬再開発）** 探索プラットフォームです。AI と大規模シミュレーションを活用し、臨床的に安全性が証明された承認薬の中から、新しい標的タンパク質に作用する候補薬を効率的に特定します。

## 🚀 主な機能

*   **構造予測**: ESMFold および AlphaFold2 による高精度な 3D タンパク質構造生成。
*   **ライブラリ自動構築**: ChEMBL API を利用した FDA 承認薬データの動的収集。
*   **バーチャルスクリーニング**: AutoDock Vina による大規模なバッチドッキング。
*   **AI 活性予測**: EGNN（同変グラフニューラルネットワーク）を用いた相互作用解析。
*   **分析ダッシュボード**: 3D 分子ビューワー、MD シミュレーション解析、LLM を活用した機序説明。

## 🛠️ セットアップ

```bash
uv venv .venv
uv pip install -r requirements.txt
```

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
Released under the [MIT License](LICENSE). Accelerating open science for rare diseases.
