# Research Report: AI 기반 중증근무력증(MG) 치료제 재창출 플랫폼
**Drug Repurposing Platform for Myasthenia Gravis using Open-Source AI**
*Version 2.0 | 2025 Q3 | Pharmaceutical & IT Expert Review*

---

## 1. 질환 개요 (Disease Overview)

중증근무력증(Myasthenia Gravis, MG)은 신경근 접합부(NMJ)에서 자가면역 기전에 의해 신호 전달이 차단되는 만성 자가면역 신경근 질환이다. 유병률은 인구 10만 명당 약 15~30명이며, 모든 연령대에서 발생 가능하나 젊은 여성과 고령 남성에서 빈도가 높다.

임상적으로 안검하수, 복시, 연하 및 호흡 곤란, 사지 근력 약화 등이 특징적으로 나타나며, 중증의 경우 Myasthenic Crisis로 진행하여 호흡 부전을 초래할 수 있다. 현재 표준 치료는 증상 완화 중심(Pyridostigmine), 면역억제(스테로이드, Azathioprine, Mycophenolate), 생물학적 제제(Eculizumab, Efgartigimod) 등이 있으나, 치료 반응성의 개인차가 크고 장기 면역억제에 따른 부작용 부담이 존재한다.

### 1.1 임상적 미충족 수요 (Unmet Medical Need)

- 약 10~15%의 환자는 현재 승인된 치료제에 반응하지 않는 치료 저항성 MG (Refractory MG)
- **MuSK-양성 MG**: AChR-양성 대비 중증 경과, 기존 치료 효과 제한적, 별도 치료 전략 필요
- 장기 스테로이드/면역억제제 사용에 따른 감염, 당뇨, 골다공증 등 이차 합병증
- 소아 MG 및 흉선종 동반 MG에 대한 전용 치료 데이터 부족
- 환자 층화(Patient Stratification) 기반 정밀의료 접근 부재

> ※ 재창출 약물 발굴은 위 미충족 수요를 해소하는 빠르고 비용 효율적인 접근법으로, 특히 희귀질환 분야에서 그 가치가 높다.

### 1.2 혈청학적 분류 및 치료 연관성

| 혈청형 (Serotype) | 빈도 (%) | 주요 항원 | 치료적 특징 | 재창출 전략 우선순위 |
|---|---|---|---|---|
| AChR-양성 | ~85% | CHRNA1 (AChR α1) | 표준 치료 반응 양호, 흉선절제 효과 있음 | AChR 안정화 / 항체 차단 |
| MuSK-양성 | ~5~8% | MuSK (MUSK) | 중증, 구인두 침범 多, Rituximab 반응 | MuSK 경로 활성화 / 보호 |
| LRP4-양성 | ~1~3% | LRP4 | 경증~중등도, 표준치료 반응 가능 | LRP4-Agrin 복합체 안정화 |
| 혈청음성 (dSN-MG) | ~5~10% | 불명 또는 복합 | 이질적, 치료 반응 예측 어려움 | 다중 표적 접근 필요 |

---

## 2. 핵심 생물학적 표적 (Key Biological Targets)

약물 재창출 전략에서 표적 단백질의 구조적·기능적 이해는 in silico 스크리닝의 정확도를 결정하는 핵심 요소다.

### 2.1 CHRNA1 – 아세틸콜린 수용체 α1 서브유닛

- **UniProt ID:** P02708 | **Gene:** CHRNA1 | **단백질 길이:** 457 aa
- **기능:** 리간드 개폐형 이온 채널(Ligand-Gated Ion Channel). ACh 결합 시 Na⁺/K⁺ 이온 유입으로 근육 탈분극 유발
- **병인 역할:** MG 환자 자가항체(IgG1, IgG3)의 주요 표적; 항체 결합 → 수용체 내재화(internalization) 및 보체 매개 파괴 → NMJ 밀도 감소
- **구조:** 펜타머 구조 (α2βγδ 또는 α2βεδ), 세포외 도메인(ECD)의 MIR(Main Immunogenic Region, α67–76)이 자가항체 핵심 에피토프
- **약물 표적 전략:**
  - MIR 에피토프에 결합하여 자가항체를 경쟁적으로 차단하는 소분자 탐색 (Competitive Epitope Blocker)
  - 이온 채널 개방 상태를 안정화하여 ACh 신호 전달 효율 증가
  - 수용체 분해 경로(ubiquitin-proteasome) 억제를 통한 수용체 발현 유지

> ※ PDB: 2QC1 (Torpedo marmorata AChR), 7QL5 (Human AChR ECD). ESMFold로 인간 전장 서열 구조 예측 시 결합 부위 비교 검증 필요.

### 2.2 MUSK – 근육특이 수용체 티로신 키나제

- **UniProt ID:** O15146 | **Gene:** MUSK | **단백질 길이:** 869 aa
- **기능:** NMJ 형성 및 유지에 필수적인 Receptor Tyrosine Kinase. Agrin-LRP4 복합체에 의해 활성화 → AChR 클러스터링 유도
- **병인 역할:** MuSK-MG에서 IgG4 자가항체가 Agrin-LRP4 결합을 방해 → MuSK 인산화 억제 → AChR 클러스터 소실
- **구조:** 세포외 CRD(Cysteine-Rich Domain)/Fz 도메인 + 단일 막관통 도메인 + 세포내 키나제 도메인 (PDB: 3HHP, 5DYN)
- **신호 경로:** MuSK → Dok-7 → Rapsyn → AChR clustering; 동시에 Wnt 신호 경로 (Fz-CRD)와 교차
- **약물 표적 전략:**
  - 키나제 도메인 활성화 컨포메이션(DFG-in)을 안정화하는 소분자 양성 조절제 (Positive Allosteric Modulator, PAM)
  - Fz-CRD 도메인을 표적으로 Wnt 독립적 MuSK 활성화 유도
  - Dok-7 결합 인터페이스 안정화를 통한 하위 신호 경로 증폭

> ※ MuSK PAM 발굴은 항체 미치료(antibody-naive) 환자뿐 아니라 MuSK-IgG4에 의해 신호가 차단된 환자 모두에서 이론적으로 치료 효과를 기대할 수 있어 전략적 가치가 높다.

### 2.3 LRP4 – 저밀도 지단백질 수용체 관련 단백질 4

- **UniProt ID:** O94898 | **Gene:** LRP4 | **단백질 길이:** 1,905 aa
- **기능:** Agrin의 공동수용체로서 MuSK와 직접 상호작용하여 신호 복합체 형성
- **병인 역할:** LRP4-MG에서 자가항체가 Agrin 결합 부위 차단 → MuSK 활성화 저하
- **표적 전략:** Agrin 결합 부위에 경쟁적으로 결합하지 않으면서 LRP4-MuSK 복합체를 안정화하는 소분자 알로스테릭 조절제

> ※ LRP4는 크기가 매우 커 ESMFold 단독 구조 예측의 신뢰도가 낮음. AlphaFold2-multimer 또는 Boltz-1을 이용한 LRP4-MuSK 복합체 구조 모델링을 강력히 권장.

### 2.4 보조 표적 (Secondary Targets) – 연구 범위 확장 권고

| 단백질 | 역할 | 재창출 근거 | 우선순위 | 현재 코드베이스 상태 |
|---|---|---|---|---|
| FcRn (FCGRT) | IgG 항체 재활용 수용체 | FcRn 차단 → 자가항체 반감기 단축 | ★★★★★ | 분석 라이브러리 포함 (준비 중) |
| C5 보체 | 보체 최종 경로 활성화 | Eculizumab 표적. 소분자 C5 억제제 탐색 | ★★★★☆ | 분석 라이브러리 포함 (준비 중) |
| Rapsyn (RAPSN) | AChR 클러스터링 단백질 | Rapsyn-AChR 결합 강화 소분자 | ★★★☆☆ | **구현 완료** (scripts/fetch_targets.py) |
| Dok-7 (DOK7) | MuSK 키나제 기질 | Dok-7 과발현 치료 효과 입증 | ★★★☆☆ | **구현 완료** (scripts/fetch_targets.py) |
| BAFF/APRIL | B세포 생존 사이토카인 | 자가항체 생성 B세포 제거 전략 | ★★★☆☆ |

---

## 3. 약물 재창출 전략 (Drug Repurposing Strategy)

### 3.1 재창출의 규제과학적 이점 및 위험

| 구분 | 재창출 (Repurposing) | 신규 개발 (De Novo) |
|---|---|---|
| 개발 기간 | 2~5년 | 10~15년 |
| 비용 | $50M~300M | $1B~2.5B+ |
| IND 신청 | 기존 독성 데이터 활용 가능 | 신규 GLP 독성시험 필요 |
| 안전성 프로파일 | 기존 임상 데이터 존재 | 완전 미지 |
| 특허 전략 | 신규 적응증 특허 (Use Patent) | 완전 신규 물질 특허 |
| 실패 위험 | PK/PD 불일치, 용량 최적화 이슈 | 임상 1~3상 전 구간 |

> ※ 재창출 약물도 희귀질환 적응증에서는 FDA Orphan Drug Designation, EMA Orphan Medicinal Product Designation을 통해 독점 판매 기간(7~10년) 확보 가능. 국내 식약처의 희귀의약품 지정 제도(법 제2조) 활용 필수 검토.

### 3.2 재창출 후보 가설 및 근거

| 약물명 | 원래 적응증 | 재창출 가설 | 분자 기전 근거 | 근거 수준 |
|---|---|---|---|---|
| Amifampridine (3,4-DAP) | LEMS | NMJ 전시냅스 강화 | 전압개폐 K⁺ 채널 차단 → ACh 분비 증가 | ★★★★★ (EMA 승인) |
| Rituximab | 류마티스관절염, B세포 림프종 | MuSK-MG 자가항체 억제 | CD20+ B세포 제거 → 자가항체 생성 감소 | ★★★★☆ (RCT 진행 중) |
| Tacrolimus (FK506) | 장기이식 거부반응 | 면역억제 + NMJ 신호 증강 | FKBP12 결합 → calcineurin 억제; 일부 연구에서 rapsyn 발현 증가 효과 | ★★★☆☆ |
| Rapamycin (Sirolimus) | 면역억제 | 조절 T세포 (Treg) 유도 | mTORC1 억제 → Treg 분화 촉진 → 자가면역 억제 | ★★★☆☆ |
| Statins (Atorvastatin) | 고지혈증 | 면역조절 / 항염증 | NFκB 경로 억제, Th17 분화 억제, AChR 발현 유지 가능성 | ★★☆☆☆ |
| Pyridostigmine | MG (기존 치료제) | 양성 대조군 | AChE 억제 → NMJ ACh 농도 증가 | ★★★★★ (표준치료) |

---

## 4. 핵심 기술 및 방법론 (Core Technologies & Methods)

### 4.1 단백질 구조 예측

| 모델 | 장점 | 단점/주의사항 | 권장 사용 시나리오 | 라이선스 |
|---|---|---|---|---|
| ESMFold | 단일 GPU 24GB에서 구동. 속도 ~30s/단량체. Meta AI transformers 통합 | 다중체(multimer) 미지원. 단량체 정확도는 AlphaFold2 대비 약간 낮음 | CHRNA1, MuSK 단량체 빠른 프로토타이핑 | MIT |
| AlphaFold2 (OpenFold) | 황금표준 단량체 예측. MSA 활용시 최고 정확도 | 다중 GPU 또는 TPU 환경 권장. MSA 생성(ColabFold 활용)이 병목 | 최고 정확도가 필요한 최종 도킹용 구조 | Apache 2.0 |
| AlphaFold2-multimer | 단백질 복합체 구조 예측. PPI 인터페이스 모델링 | 고사양 GPU 필요, 실행 시간 증가 | LRP4-MuSK, AChR 펜타머 복합체 | Apache 2.0 |
| Boltz-1 (MIT) | AlphaFold3 수준 성능, 소분자-단백질 복합체 예측 | 최신 모델로 커뮤니티 검증 진행 중 | 단백질-리간드 공동 구조 예측 (co-folding) | MIT |
| RoseTTAFold2 | 단량체 및 복합체 균형잡힌 성능 | 설치 복잡, 메모리 요구량 높음 | 크로스체크용 대안 모델 | BSD-3 |

> ※ **실무 권고:** ESMFold로 빠른 1차 구조 생성 → AutoDock Vina로 초기 스크리닝 → 상위 20위 후보에 한해 AlphaFold2 고정밀 구조 재예측 후 재도킹(2-stage screening). 이 접근법이 계산 비용 대비 효율을 최대화한다.

### 4.2 분자 도킹 및 가상 스크리닝

- **AutoDock Vina 1.2+**: PyMOL/ADFRsuite와 통합, SMINA(AutoDock Vina fork) 사용 시 scoring function 개선 가능
- **리간드 준비 파이프라인:**
  - RDKit → 3D 컨포머 생성 (ETKDG + MMFF94 에너지 최소화, 최소 10개 컨포머 생성 후 최저 에너지 선택)
  - Meeko 또는 ADFRsuite → .pdbqt 변환 (비공유 전자쌍 및 회전 가능 결합 처리)
  - Pan-ADMET 사전 필터링: Lipinski Rule-of-5, TPSA < 140Å², MW 150~500 Da
- **결합 포켓 정의:**
  - CHRNA1: ECD의 Orthosteric site (α/δ 인터페이스) 및 MIR 에피토프 주변 알로스테릭 부위
  - MuSK: ATP 결합 포켓 (hinge region: Met605, Leu624) 및 Fz-CRD 소수성 groove
  - FPOCKET 또는 SiteMap(Schrödinger free tier)을 이용한 포켓 탐지 자동화
- **결합 친화도 해석 기준 (kcal/mol):**
  - `< −8.0` : 강한 결합 (Hit 기준, 상위 후보)
  - `−6.0 ~ −8.0` : 중등도 결합 (검토 필요)
  - `> −6.0` : 약한 결합 (폐기)

> ※ Vina 점수만으로는 false positive가 많음. MM-GBSA 재채점(rescoring)을 상위 50위 이내 후보에 적용하여 예측 정확도 향상을 강력히 권장함 (AmberTools 사용 가능, 무료).

### 4.3 AI 활성 예측 모델 (GNN / EGNN)

단순 도킹 점수는 결합 친화도를 근사하지만, 약물의 기능적 효과(작용제/길항제)를 예측하지 못한다. EGNN 기반 AI 모델은 단백질-리간드 복합체의 3D 그래프 표현으로부터 기능적 활성을 예측한다.

- **EGNN 입력 특징:**
  - 노드 특징: 원자 유형(one-hot), 공식 전하, 혼성화 상태, 방향족성, 수소 결합 공여/수용 여부
  - 엣지 특징: 결합 유형, 공간적 거리, 이면각(dihedral angles)
  - 3D 좌표: 회전/병진 불변성(E(3)-equivariance) 보장
- **사전 학습 데이터셋:**
  - BindingDB: ~2.8M개 단백질-리간드 결합 친화도 데이터
  - ChEMBL assay 데이터: 이온 채널(CHRNA1 계열) 및 키나제(MuSK) 활성 데이터
  - ExCAPE-DB: 1,550만 개 화합물-표적 활성 데이터 (무료 다운로드 가능)
- **파인튜닝 전략:** MG 관련 assay (ChEMBL 기준 target_chembl_id: CHEMBL4296141 [CHRNA1], CHEMBL4523582 [MUSK]) 데이터 추출 후 transfer learning
- **대안 모델:** DeepPurpose (MIT 오픈소스), DGraphDTA, KDeep – 설치 및 사용이 상대적으로 간단

> ※ EGNN 자체 구현에 과도한 개발 시간을 투자하기 전에, DeepPurpose 또는 DGraphDTA를 baseline으로 먼저 구동하여 개념 검증(PoC) 수행을 권장. 자체 EGNN 구현은 Phase 2 이후로 배치하는 것이 현실적.

---

## 5. 데이터 소스 (Free APIs & Databases)

| 데이터베이스 | 제공 데이터 | API 유형 | MG 활용 방법 | 중요 고려사항 |
|---|---|---|---|---|
| ChEMBL 34 | 2M+ 생체활성 화합물, assay 데이터 | REST / SQLite 다운로드 | CHRNA1, MUSK target ChEMBL ID로 활성 화합물 조회. FDA 승인 필터 (max_phase=4) | 데이터 품질 이질성 (IC50 vs Ki vs % inhibition). 단위 통일 필수 |
| UniProt | 단백질 서열, 기능 어노테이션, PDB 매핑 | REST | FASTA 서열, 기능 도메인 위치, PTM 사이트 조회 | 알파폴드 구조 링크 활용. 이소폼(isoform) 구별 필요 |
| PubChem | 1억+ 화합물, 생물활성 데이터 | REST / FTP | CID 기반 SMILES, InChIKey 조회. MG 관련 bioassay 필터링 | ChEMBL과 중복 데이터 있음. 통합 시 중복 제거 필요 |
| Open Targets | 표적-질환 연관성 점수, 유전체 증거 | GraphQL | MG (EFO_0000751) 연관 표적 우선순위화, 유전적 증거 등급 확인 | 증거 점수는 통계적 연관성이며 인과성을 보장하지 않음 |
| RCSB PDB | 실험적 단백질 구조 (X-ray, CryoEM) | REST | CHRNA1, MuSK 결정 구조 다운로드. 도킹 기준 구조로 활용 | 해상도 및 리간드 공결정 여부 확인 필수 (< 2.5Å 권장) |
| DrugBank | 약물 메커니즘, 상호작용, 대사 | XML 다운로드 (무료 등록) | ATC 코드, 표적 단백질 매핑, 약물-약물 상호작용 데이터 | Academic license 무료. 상업적 사용 제한 확인 |

---

## 6. ADMET 및 독성 예측 (In Silico ADMET)

유효한 도킹 점수를 가진 히트(hit) 화합물이라도 부적절한 약동학(PK) 또는 독성 프로파일로 인해 개발에 실패하는 경우가 전체 신약 개발 실패의 약 40%를 차지한다.

| 예측 항목 | 오픈소스 도구 | 주요 필터 기준 | MG 특이 고려사항 |
|---|---|---|---|
| BBB 투과성 | pkCSM, SwissADME (무료 웹) | logBB > −1 (중추 목표시 필요) | 말초 NMJ 표적 약물은 낮은 BBB 투과성이 오히려 선호됨 (CNS 부작용 최소화) |
| CYP 억제 | ADMETlab 2.0, pkCSM | CYP3A4/2D6 억제 없어야 함 | Pyridostigmine과의 CYP 상호작용 검토 필수 (병용 가능성 고려) |
| hERG 독성 | DeepHit, cardiotoxpred | IC50 hERG > 10μM | MG 환자는 심장 합병증 동반 多 → 부정맥 리스크 특히 중요 |
| 간독성 (DILI) | DILIrank, pkCSM | DILI 예측 음성 | 장기 면역억제제 병용 고려 시 간 독성 부담 최소화 필요 |
| 구강 생체이용률 | SwissADME, Lipinski RO5 | F > 30% 목표 | 경구 복용 가능성은 환자 순응도에 직결 |
| Pan-Assay Interference (PAINS) | RDKit PAINS filter | PAINS 패턴 없어야 함 | 고반응성 기능기(reactive group)는 false-positive 도킹 결과를 유발 |

---

## 7. 규제 및 윤리 고려사항 (Regulatory & Ethical Considerations)

### 7.1 비임상(in silico) 연구 한계 및 투명성

- AI 기반 in silico 예측은 실험적 검증의 대체재가 아닌 **가설 생성 도구**임을 명확히 해야 한다.
- 도킹 점수 해석 시 결정론적 판단을 피하고, 통계적 불확실성(uncertainty quantification)을 함께 보고해야 한다.
- AI 모델 훈련에 사용한 데이터셋, 모델 가중치, 스크리닝 파이프라인 코드는 재현성을 위해 GitHub에 공개(MIT/Apache 라이선스)를 원칙으로 한다.

### 7.2 지식재산권 (IP) 전략

- 오픈소스 도구(ESMFold, AutoDock Vina, RDKit)를 이용한 결과물 자체는 도구 라이선스의 제약을 받지 않으나, 도구별 라이선스 조건(특히 상업적 이용 가능 여부) 확인 필수
- 히트 화합물의 MG 적응증 재창출 발견에 대한 **방법 특허(Method Patent)** 또는 **용도 특허(Use Patent)** 가능성 검토
- 스크리닝 파이프라인 자체에 대한 소프트웨어 특허 또는 영업비밀(Trade Secret) 전략 병행 고려

### 7.3 IRB/IBC 고려사항

- 순수 in silico 연구는 IRB 심의 불요. 단, 연구 결과를 바탕으로 한 세포 실험(in vitro) 또는 동물 실험(in vivo) 단계 진입 시 즉시 기관 심의 필요
- 인체 유래 생체시료(환자 혈청, 세포주 등) 활용 시 IRB 승인 및 생명윤리법 준수 의무화

---

## 8. 검증 로드맵 (Validation Roadmap)

| 단계 | 방법론 | 목표 지표 | 예상 소요 기간 | 비용 수준 |
|---|---|---|---|---|
| 1. In silico (현 단계) | AutoDock Vina + EGNN 활성 예측 + ADMET 필터링 | 결합 친화도 < −8 kcal/mol, ADMET 통과 | 2~4주 | 무료 (오픈소스) |
| 2. In vitro – Binding Assay | SPR (표면 플라즈몬 공명), ITC (등온 적정 열량계) | Kd < 1 μM, Hit rate > 0.5% | 2~3개월 | 저~중간 |
| 3. In vitro – Functional Assay | Patch-clamp (AChR 이온 채널 활성), HTRF 인산화 측정 (MuSK) | EC50/IC50, 작용/길항 확인 | 3~4개월 | 중간 |
| 4. In vitro – Cell Model | C2C12 근모세포, iPSC 유래 근육세포 + AChR 항체 처리 MG 모델 | AChR 클러스터 면적, NMJ 마커 발현 | 4~6개월 | 중간 |
| 5. In vivo – 동물 모델 | EAMG (실험적 자가면역 MG) 쥐 모델 | 임상 점수, AChR 항체 역가, NMJ 조직학 | 6~12개월 | 높음 |
| 6. IND 신청 준비 | GLP 독성시험(급성/반복독성, 생식독성, 유전독성) | NOAEL 설정, 독성 프로파일 | 18~24개월 | 매우 높음 |

---

## 9. 참고 문헌 및 핵심 자료

| 분류 | 주요 참고자료 |
|---|---|
| 임상 가이드라인 | Myasthenia Gravis Foundation of America (MGFA) Clinical Classification; Narayanaswami et al., Neurology 2021 MG Treatment Guidelines |
| 구조 생물학 | Unwin N. J Mol Biol 2005 (AChR 구조); Stiegler AL, Bhatt DK J Mol Biol 2018 (MuSK 키나제) |
| AI 구조 예측 | Lin Z et al. Science 2023 (ESMFold); Jumper J et al. Nature 2021 (AlphaFold2) |
| 약물 재창출 방법론 | Pushpakom S et al. Nat Rev Drug Discov 2019 (재창출 리뷰); Zeng X et al. Nat Commun 2022 (MG AI 스크리닝) |
| GNN/EGNN | Satorras VG et al. ICML 2021 (EGNN); Kearnes S et al. J Chem Inf Model 2016 (MoleculeNet) |
| ADMET | Daina A et al. J Chem Inf Model 2017 (SwissADME); Yang K et al. J Chem Inf Model 2019 (Chemprop) |

---

*본 문서는 내부 연구 목적으로만 사용되며, 외부 공개 시 별도 승인이 필요합니다.*
