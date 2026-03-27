<div align="center">

<img src="https://github.com/danjjak-ai/alphafold-drug-platform/blob/master/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202026-03-20%20151436.png" alt="Discovery Core Banner" width="800"/>

# 🧬 Discovery Core (RareTarget Discovery)

### AI-Powered Drug Repurposing Platform for Rare Neuromuscular Disease
**중증근무력증(MG) 치료제 재창출을 위한 AI 시뮬레이션 및 데이터 파이프라인**

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

---

## 💻 시스템 요구사항 (Requirement)
본 플랫폼은 로컬 환경에서의 구동을 위해 최적화되었습니다.

| 구분 | 최소 사양 | 권장 사양 |
|---|---|---|
| **GPU** | NVIDIA GPU 8GB VRAM | NVIDIA RTX 3090/4090 24GB |
| **RAM** | 32 GB | 64 GB 이상 |
| **OS** | Windows 10/11 (uv 필수) | Ubuntu 22.04 LTS |

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
| **Phase 3** | AI 활성 예측 모델 | **진행 중** | GCN/RF 모델 기반 활성 추론 |
| **Phase 4** | LLM RAG 기반 기전 설명 | **미구현** | LangChain/ChromaDB 연동 예정 |
| **Phase 5** | MM-GBSA 정밀 재채점 | **미구현** | AmberTools 기반 스코어 보정 예정 |
| **Phase 6** | 최종 결과 보고서 자동화 | **미구현** | PDF 및 분석 리포트 생성 기능 |

---

## 🛠️ 설치 및 실행 (Installation)

### 1. 환경 설정
```bash
# uv 설치 (https://astral.sh/uv)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 가상환경 생성 및 패키지 설치
uv venv .venv
uv pip install -r requirements.txt
```

### 2. 실행
```bash
# 전체 파이프라인 실행 (Windows)
run_pipeline.bat

# 대시보드만 실행
start_dashboard.bat
```
접속 URL: **http://localhost:8501**

---

# 🇺🇸 English

## 📖 Overview
**Discovery Core** is an integrated platform designed to accelerate **drug repurposing** for rare neuromuscular diseases, specifically Myasthenia Gravis (MG). By combining pharmaceutical expertise with cutting-edge AI, we explore the potential of existing FDA-approved drugs against novel targets like **CHRNA1**, **MuSK**, and **LRP4**.

## 🚀 Key Features
- **In Silico Screening**: Batch molecular docking using AutoDock Vina.
- **AI-Based Prediction**: Activity inference using GCN (Graph Convolutional Networks).
- **Interactive UI**: High-fidelity 3D visualization using 3Dmol.js and Tailwind CSS.
- **Workflow Automation**: Full data pipeline from protein structure prediction to analytics.

## 🗺️ Implementation Roadmap
- [x] **Phase 1**: Data Pipeline (ChEMBL, UniProt, SQLite)
- [x] **Phase 2**: Virtual Screening (AutoDock Vina)
- [x] **Phase 3**: AI Activity Scoring (Baseline GCN implemented)
- [ ] **Phase 4**: LLM-Powered Biological Insights (RAG System - **Unimplemented**)
- [ ] **Phase 5**: MM-GBSA Precision Rescoring (**Unimplemented**)
- [ ] **Phase 6**: Automated Analytical Reporting (**Unimplemented**)

---

# 🇯🇵 日本語

## 📖 概要
**Discovery Core** は、希少神経筋疾患（主に重症筋無力症）に対する **既存薬再開発（ドラッグリパーパシング）** を加速させるための AI 統合プラットフォームです。

## 🚀 主な機能
- **仮想スクリーニング**: AutoDock Vina による大規模ドッキングシミュレーション。
- **AI 活性予測**: GCN（グラフニューラルネットワーク）を用いた相互作用解析。
- **インタラクティブ分析**: Streamlit と 3Dmol.js を活用した解析ダ미ボード。

## 🗺️ 実装ステータス
- [x] **Phase 1~2**: データ収集およびドッキング（実装済み）
- [x] **Phase 3**: AI 予測モデル（ベースライン実装済み）
- [ ] **Phase 4~6**: LLM RAG システム、MM-GBSA 精密計算、自動レポート（**未実装**）

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
