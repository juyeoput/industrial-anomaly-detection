"""Generate the Korean project overview aligned with fault document v6."""

from pathlib import Path


OUTPUT_PATH = Path(__file__).resolve().with_name("project_overview_kr.md")

DOCUMENT = """
# 프로젝트 전체 개요 및 역할 가이드 v6
## 작성: 윤서 (화학공학)
## 대상: 주엽 (ML 모델 개발), 현범 (운영·최적화)

---

## 1. 우리가 만드는 시스템

한 줄 요약:

**TEP 공정 센서 데이터를 분석해 이상을 감지하고, Fault 유형과 근거 센서를 제시하며, LLM이 불확실성을 포함한 설명과 진단 점검 항목을 제공하는 산업 이상 감지 시스템이다.**

단순 경보 시스템은 센서가 임계값을 넘었다는 사실만 알려준다. 우리 프로젝트는 다음 단계를 연결하는 것이 목표다.

```text
센서 시계열
  -> 이상 감지
  -> Fault 분류
  -> 핵심 센서와 시간 패턴 제시
  -> LLM 설명
  -> 운영 KPI 및 대응 우선순위 검토
```

LLM의 설명은 자동 운전 명령이나 실제 공장 안전 절차가 아니다. 모델과 데이터가 제공한 근거를 사람이 이해하기 쉽게 설명하는 보조 수단이다.

---

## 2. 왜 Tennessee Eastman Process를 사용하는가

실제 공장 데이터는 기업 기밀이고 실제 Fault 사례도 충분히 확보하기 어렵다. Tennessee Eastman Process(TEP)는 정상 운전과 여러 Fault 시나리오를 포함한 화학 공정 시뮬레이션 데이터로, 산업 이상 감지 연구에서 널리 사용되는 벤치마크다.

TEP는 다음 5개 주요 공정 단위로 구성된다.

- **반응기(Reactor)**: 발열 반응이 진행되며 온도와 압력을 제어한다.
- **응축기(Condenser)**: 반응기 상부 증기를 냉각한다.
- **기액분리기(Separator)**: 기체 재순환 유체와 액체를 분리한다.
- **재순환 압축기(Compressor)**: 분리된 기체를 반응기로 재순환한다.
- **스트리퍼(Stripper)**: 가벼운 성분을 제거해 제품을 정제한다.

데이터의 기본 구조는 다음과 같다.

- 측정 간격: 3분
- 측정 변수: `xmeas_1`~`xmeas_41`
- 조작 변수: `xmv_1`~`xmv_11`
- 공정 변수 합계: 52개
- 메타데이터: `faultNumber`, `simulationRun`, `sample`
- Testing 데이터 Fault 시작 시점: sample 160, 약 8시간
- Training 데이터 Fault 시작 시점: sample 20

---

## 3. 프로젝트에서 다루는 Fault

현재 문서와 EDA는 전체 20개 Fault 중 다음 10개를 우선 분석한다.

| Fault | 주요 영역 | V6에서 확인한 핵심 패턴 |
|------:|-----------|-------------------------|
| 1 | Feed | `xmeas_1`과 `xmeas_4`의 크고 지속적인 평균 이동 |
| 2 | Composition | 초기 조성 변동성과 후기 purge 조성 평균 이동 |
| 4 | Reactor cooling | `xmv_10`의 지속적인 평균 증가와 제어 보상 |
| 6 | Feed loss | A-feed의 거의 완전한 손실과 후기 고정·포화 상태 |
| 7 | Feed pressure | 초기 transient와 후기 잔류 변동성 |
| 8 | Feed composition | 평균 방향은 Run마다 다르지만 다변량 변동성은 지속 |
| 11 | Reactor cooling | 평균보다 `xmeas_9`, `xmv_10`의 불규칙 변동성 증가가 중요 |
| 12 | Separator cooling | 분리기 측 온도·압력·냉각수 변수의 혼합 반응 |
| 13 | Reaction kinetics | 반응기 압력의 강한 변동성과 후기 평균 성분 |
| 14 | Reactor CW valve | 반응기 온도와 냉각수 출구 온도의 지속적인 고변동성 |

이번 범위에서 제외한 Fault는 3, 5, 9, 10, 15, 16, 17, 18, 19, 20이다. 제외된 Fault가 중요하지 않다는 의미는 아니며, 현재 프로젝트 범위를 제한한 것이다.

---

## 4. 윤서가 완료한 작업: Phase 1~2

### 4.1 공정 및 변수 해석

- 41개 XMEAS와 11개 XMV의 이름, 단위, 정상 범위, 물리적 의미 정리
- 반응기, 분리기, 냉각 계통, Feed 계통의 주요 변수 연결
- 모델이 숫자만 학습하지 않고 공정적 의미를 확인할 수 있는 기준 마련

### 4.2 그래프 기반 EDA

- 선택한 10개 Fault에 대해 정상 Run과 Fault Run 비교 그래프 생성
- Fault 시작 시점인 sample 160 전후의 변화 확인
- 초기 반응, 지속 반응, 진동·변동성 반응을 시각적으로 구분

그래프는 대표적인 Run 1의 사례다. 모든 Run에서 동일한 궤적이 나타난다는 증명으로 사용하지 않는다.

### 4.3 50-Run 공정 변수 검증

V6에서는 각 simulation Run을 하나의 독립 관측치로 사용했다. 정상 데이터와 Fault 데이터는 반드시 동일한 sample 구간에서 비교했다.

| Window | Sample | 목적 |
|--------|--------|------|
| Early | 160~260 | Fault 직후의 초기·transient 반응 확인 |
| Late | 300~960 | 초기 반응 이후 지속되는 변화 확인 |
| Full | 160~960 | 전체 Fault 구간의 종합 반응 확인 |

Run별로 다음 값을 계산했다.

- 평균 변화율
- 정상 표준편차로 정규화한 평균 차이
- 표준편차 비율
- 평균 변화 방향의 Run 간 일관성
- 분산 증가 Run 비율
- Run별 paired difference에 대한 one-sample t-test
- Wilcoxon signed-rank test

이 결과는 `fault_run_level_validation.csv`에 저장되어 있다. p-value는 보조 근거이며, 센서 선택은 효과 크기, 방향 일관성, 시간 지속성, 물리적 타당성을 먼저 확인한다.

### 4.4 Fault 2 조성 센서 10-Run 검증

다음 4개 조성 센서를 Early, Late, Full 구간에서 비교했다.

- `xmeas_24`: Reactor Feed B Composition
- `xmeas_30`: Purge B Composition
- `xmeas_35`: Purge G Composition
- `xmeas_40`: Product G Composition

주요 결과는 다음과 같다.

- `xmeas_30`: 초기 구간에서 큰 평균 변화와 변동성 증가
- `xmeas_24`: 초기 구간에서 강한 조성 반응을 보이고 후기에는 대부분 감소
- `xmeas_35`: 후기 구간에서 지속적인 평균 증가
- `xmeas_40`: 분석한 10개 Run에서는 유의미한 차이가 관찰되지 않음

`xmeas_40` 결과는 해당 표본 Run에서 차이가 관찰되지 않았다는 뜻이며, 제품 품질이 어떤 상황에서도 영향을 받지 않는다는 증명은 아니다.

### 4.5 최종 도메인 문서 V6

`fault_scenario_document_v6.md`에는 다음 내용이 포함되어 있다.

- TEP 공정과 52개 공정 변수 정의
- 검증 방법과 근거 수준
- 50-Run 공정 변수 결과
- Fault 2 조성 센서 10-Run 결과
- Fault별 주요 센서와 시간 패턴
- 비슷한 Fault를 구별하는 기준
- 모델 Feature 설계 가이드
- LLM 설명 시 지켜야 할 불확실성 원칙
- 데이터 누수 방지와 모델 평가 요구사항

---

## 5. 분석 파일의 역할

| 파일 | 역할 |
|------|------|
| `config.py` | Fault별 분석 센서와 그래프 제목 정의 |
| `plot_fault.py` | 데이터 로드 및 정상·Fault 그래프 생성 |
| `run_all.py` | 선택한 모든 Fault 그래프 일괄 생성 |
| `fault_run_level_validation.py` | 50-Run 공정 변수 검증 실행 |
| `fault_run_level_validation.csv` | 50-Run 검증 결과 |
| `fault2_composition.py` | Fault 2 조성 센서 10-Run 분석 |
| `fault2_composition_multi_run_summary.csv` | Fault 2 조성 분석 결과 |
| `fault_scenario_document_v6.py` | 최신 CSV를 이용해 V6 정량 표 갱신 |
| `fault_scenario_document_v6.md` | 주엽이에게 전달할 최신 도메인 문서 |
| `images/` | 대표 Run의 시각적 EDA 결과 |

V3~V5 문서와 기존 단일 Run 통계 파일은 분석 발전 과정을 보여주는 변경 이력이다. 최신 결론의 근거로는 V6와 Run-level CSV를 사용한다.

---

## 6. 주엽의 역할: Phase 3 모델 개발

### 6.1 데이터 분할과 누수 방지

- 행 단위가 아니라 `simulationRun` 단위로 train, validation, test를 분리한다.
- 같은 Run에서 만든 행이나 겹치는 시계열 Window가 서로 다른 Split에 들어가면 안 된다.
- Fault Run의 sample 160 이전 구간은 정상 Label로 사용할 수 있지만 전체 Run은 하나의 Split에만 둔다.
- Scaler와 학습형 전처리는 정상 training Run에만 fit한다.
- 최종 test Run은 모델과 Threshold가 확정될 때까지 사용하지 않는다.

### 6.2 이상 감지

- 정상 training Run을 이용해 정상 패턴을 학습한다.
- 이상 점수 Threshold는 정상 validation Run에서 목표 false-positive rate에 맞춰 설정한다.
- Fault test 데이터를 이용해 Threshold를 조정하지 않는다.

초기 기준 모델로 Isolation Forest 또는 Autoencoder를 비교할 수 있다. 단, 모델 이름보다 데이터 누수 방지와 평가 방식이 더 중요하다.

### 6.3 Fault 분류

- Fault가 감지된 뒤 Fault 번호를 분류하는 supervised classifier를 학습한다.
- 초기 기준 모델로 Random Forest를 사용하고, 필요하면 LSTM 등 sequence 모델과 비교한다.
- Fault 4와 11, Fault 12와 14, Fault 7과 8의 혼동을 별도로 확인한다.

### 6.4 Feature 설계

평균값만 사용하면 Fault 8, 11, 12, 13, 14와 Fault 7의 후기 반응을 놓칠 수 있다. 다음 Feature를 함께 검토한다.

- 원본 정규화 센서값
- Rolling mean
- Rolling standard deviation
- Rolling range
- 변화율
- 필요할 경우 spectral 또는 sequence feature
- Fault 2용 조성 센서 `xmeas_24`, `xmeas_30`, `xmeas_35`
- Fault 4와 11 구분을 위한 `xmv_10`

52개 전체 변수를 사용한 모델과 EDA 선택 Feature 모델을 ablation study로 비교한다.

### 6.5 필수 평가 지표

- 정상 test Run의 false-alarm rate
- Fault별 recall, precision, F1-score
- Confusion matrix
- sample 160 이후 detection delay
- Fault 2와 Fault 7의 Early·Late 구간별 성능
- Run별 결과 분포 또는 신뢰구간

Accuracy 하나만 보고 모델 성능을 판단하지 않는다.

---

## 7. 모델 개발 중 윤서의 역할

윤서의 EDA 제작 단계는 거의 완료되었다. 모델 개발 중에는 다음 도메인 검증을 담당한다.

1. 모델이 선택한 핵심 센서가 공정적으로 타당한지 검토
2. Fault 4와 11처럼 같은 냉각 계통 Fault가 올바르게 구분되는지 확인
3. Fault 12와 14가 분리기 측·반응기 측 패턴으로 구별되는지 확인
4. Fault 7의 초기 transient와 후기 잔류 변동성이 감지되는지 확인
5. Fault 6의 후기 0분산 상태를 정상 회복으로 잘못 판단하지 않는지 확인
6. Fault 2에서 조성 센서가 실제 분류 성능을 개선하는지 ablation 결과 검토
7. LLM 설명이 관찰 결과와 추론을 구분하는지 확인
8. 모델 오류 사례를 다시 EDA해 V6 문서의 한계를 업데이트

이 단계에서 중요한 것은 그래프를 무한히 추가하는 것이 아니라, 모델의 오탐과 미탐을 공정 지식으로 해석하는 것이다.

---

## 8. 현범의 역할: 운영 및 최적화

현범은 모델 결과를 운영 관점의 지표와 연결한다.

- Fault 전후 throughput, quality 관련 변수, 에너지 사용량 변화 분석
- Fault별 운영 영향과 유지보수 우선순위 비교
- 이상 감지가 KPI 저하 전에 발생하는지 검토
- 대시보드용 KPI와 추세 지표 설계
- 모델의 감지 결과를 사용한 시나리오 기반 대응 비교

TEP 데이터만으로 실제 OEE나 경제 손실을 직접 계산할 경우 추가 가정이 필요하다. 가정한 값은 실제 측정값과 명확히 구분해야 한다. 운영 대응은 검토용 시나리오이며 실제 공장 운전 지침이나 안전 절차가 아니다.

---

## 9. LLM 연동 원칙

LLM은 원시 센서만 보고 독립적으로 Fault를 진단하지 않는다. 모델이 제공한 후보 Fault, 확률, 이상 점수, 핵심 Feature와 V6 문서를 근거로 설명한다.

LLM 출력에는 다음 항목이 포함되어야 한다.

1. 가장 가능성 높은 Fault와 모델의 보정된 신뢰도
2. 판단에 사용한 센서와 Feature
3. Mean shift, variance, transient 등 시간 패턴
4. 관찰된 사실과 공정적 추론의 구분
5. 경쟁 가능한 다른 Fault와 불확실성
6. 자동 운전 명령이 아닌 진단 점검 항목

LLM은 존재하지 않는 측정값, 밸브 설정값, 안전 절차를 만들어내면 안 된다. `pattern consistent with`에 해당하는 신중한 표현을 사용한다.

---

## 10. 현재 프로젝트 상태

| 단계 | 담당 | 상태 |
|------|------|------|
| 데이터 확보 및 구조 확인 | 윤서 | 완료 |
| 10개 Fault 그래프 EDA | 윤서 | 완료 |
| 50-Run 공정 변수 검증 | 윤서 | 완료 |
| Fault 2 조성 센서 10-Run 검증 | 윤서 | 완료 |
| Fault Scenario Document V6 | 윤서 | 완료 |
| 이상 감지 기준 모델 | 주엽 | 진행 예정 또는 진행 중 |
| Fault 분류 모델 | 주엽 | 진행 예정 |
| LLM 설명 모듈 | 주엽·윤서 | 모델 결과 후 진행 |
| KPI·운영 영향 분석 | 현범 | 모델 결과와 병행 |
| 통합 대시보드 | 팀 공동 | 후속 단계 |

윤서의 Phase 1~2는 사실상 완료되었으며, 이후 핵심 역할은 모델 결과의 도메인 검증과 문서 보완이다.

---

## 11. 주엽에게 전달할 파일

최소 전달 묶음은 다음과 같다.

1. `fault_scenario_document_v6.md`
2. `fault_run_level_validation.csv`
3. `fault2_composition_multi_run_summary.csv`
4. `config.py`
5. `plot_fault.py`
6. `fault_run_level_validation.py`
7. `fault2_composition.py`
8. `images/`의 주요 Fault 그래프

V3~V5, `fault_sensor_summary.csv`, `fault_ttest_summary.csv`는 변경 이력과 탐색용 자료로 보관하되 최신 통계 근거로 사용하지 않는다.

---

## 12. 분석의 한계

- 전체 20개 Fault 중 10개만 상세 분석했다.
- 그래프는 대표 Run 1을 보여준다.
- 공정 변수 검증은 500개 전체가 아닌 50개 표본 Run을 사용했다.
- Fault 2 조성 검증은 4개 센서와 10개 표본 Run에 한정된다.
- 다수의 통계 검정을 수행했으므로 p-value만으로 Feature를 선택하면 안 된다.
- 시뮬레이션 결과를 실제 공장의 안전성, 위험도, 운전 절차로 직접 일반화할 수 없다.
- 최종 결론은 held-out Run에서의 모델 성능과 오류 분석을 통해 다시 검토해야 한다.

---

## 13. 다음 작업

1. 주엽이 Run 단위 Split을 확정한다.
2. 정상 데이터 기반 이상 감지 Baseline을 만든다.
3. Fault별 recall, false-alarm rate, detection delay를 공유한다.
4. 윤서가 오탐·미탐 사례를 공정 관점에서 검토한다.
5. 현범이 Fault 전후 KPI와 운영 영향을 연결한다.
6. 검증된 모델 결과를 LLM과 대시보드에 연동한다.

이 문서는 프로젝트 진행 상황과 역할을 설명하는 한국어 개요다. 정량 근거와 Fault별 상세 설명은 `fault_scenario_document_v6.md`와 최신 CSV를 우선 참고한다.
""".strip()


def main() -> None:
    OUTPUT_PATH.write_text(DOCUMENT + "\n", encoding="utf-8")
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
