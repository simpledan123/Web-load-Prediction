# AI 운동 웹 서비스 부하 예측 및 동적 인프라 확장 시스템

## 1. 프로젝트 개요 및 목표

이 프로젝트는 **PostgreSQL DB**에 저장되는 AI 운동 웹 서비스의 트래픽 데이터(API 호출량)를 분석하고, **Prophet AI 모델**로 미래 부하를 예측하여 인프라 자원을 **자동으로 확장/축소(Scale-up/Down)**함으로써 서비스의 운영 안정성과 비용 효율성을 확보하는 **데이터 엔지니어링 및 DevOps 시뮬레이션** 프로젝트입니다.

### 핵심 목표

* **안정성 확보:** 트래픽 피크 전에 AI 예측을 기반으로 서버를 미리 확장하여 서비스 장애를 예방.
* **비용 효율:** 부하가 낮을 때 유휴 자원을 자동으로 축소하여 운영 비용을 절감.
* **통합 증명:** DB 구축부터 AI 로직, TypeScript UI까지 이어지는 **전체 데이터 파이프라인 구축 능력**을 입증.

---

## 2. 기술 스택 (Tech Stack)

| 영역 | 기술 | 역할 |
| :--- | :--- | :--- |
| **데이터 및 DB** | **PostgreSQL**, SQLAlchemy, Pandas | 웹 로그 저장, SQL 분석, Python 데이터 연동. |
| **AI 모델링** | **Prophet** | 시계열 트래픽 부하 예측 모델 구축 및 성능 검증. |
| **시스템/자동화** | **Python** | 예측값을 기반으로 서버 규모를 결정하는 동적 확장 로직 구현. |
| **프론트엔드/시각화** | **Streamlit**, Plotly, **TypeScript** | AI 예측 및 인프라 상태를 시각화하는 인터랙티브 대시보드 구축. |

---

## 3. 아키텍처 및 데이터 흐름

프로젝트는 DB를 통해 모든 구성 요소가 연결되는 모듈식 구조입니다.

**데이터 흐름:**

1.  **데이터 소스:** `01_Data_Processing`에서 가상 데이터를 생성하여 **PostgreSQL DB**의 `traffic_log` 테이블에 적재.
2.  **AI 예측:** `02_AI_Model_Development`에서 DB 데이터 (`ds`, `y`)를 읽어 Prophet 모델 학습 및 다음 7일 부하 예측.
3.  **동적 스케일링:** `03_Scaling_Logic`에서 AI 예측 결과를 기반으로 최적 서버 수를 계산하고 시뮬레이션 결과 CSV 생성.
4.  **프론트엔드:** `04_Frontend`에서 시뮬레이션 결과를 읽어 Streamlit 대시보드를 통해 시각화.

---

## 4. 실행 지침 (프로젝트 재현 방법)

### A. 환경 준비 (필수 선행 작업)

1.  **PostgreSQL 설치** 및 DB 비밀번호 설정.
2.  pgAdmin에서 DB(`AI_WebLoad_DB`)와 테이블(`traffic_log`) 생성.
3.  Node.js 및 npm 설치.
4.  모든 Python 파일(`web_traffic_simulator.py`, `model_training.py`, `sql_analytics.py`)의 **DB_PASS** 변수를 본인의 DB 비밀번호로 **수정**.

### B. Python 환경 및 라이브러리 설치

프로젝트 루트 폴더(`AI_WebLoad_Prediction_System`)에서 실행합니다.


# 가상 환경 활성화 (Windows 기준)
.\venv\Scripts\activate

C. TypeScript 컴포넌트 빌드
Streamlit 앱 실행 전, TypeScript 컴포넌트 파일을 빌드합니다.

# 1. frontend 폴더로 이동
cd 04_Frontend/ts_component/frontend

# 2. 빌드 실행
npm run build

# 3. 프로젝트 루트로 복귀
cd ../../..

D. 프로젝트 순차 실행
PostgreSQL 서버가 실행 중인 상태에서 순서대로 실행합니다.

순서,폴더,명령어,역할
1.,01_Data_Processing,python web_traffic_simulator.py,가상 데이터 생성 및 DB 적재
2.,01_Data_Processing,python sql_analytics.py,DB에서 데이터 읽어 분석 그래프 생성
3.,02_AI_Model_Development,python model_training.py,DB 데이터로 Prophet 학습 및 예측 CSV 생성
4.,03_Scaling_Logic,python dynamic_scaler.py,AI 예측 기반 서버 확장 로직 실행
5.,04_Frontend,streamlit run dashboard_app.py,최종 대시보드 실행 및 결과 시각화

5. 주요 결과 및 성과
그래프 시연: 대시보드의 'AI 예측 부하 vs. 동적 확장 액션' 그래프를 통해 AI 예측이 서버 증설(Scale-up)을 미리 트리거하여 안정성을 확보하는 과정을 시각적으로 증명.

효율성 입증: KPI 지표를 통해 정적 할당 대비 서버 사용 시간 절감 비율을 정량적으로 제시.

기술 통합: Python과 TypeScript가 Streamlit을 통해 상호 작용하며, AI 백엔드 결과가 UI에 실시간으로 반영되는 풀 스택 시뮬레이션 구현.

# 필수 Python 라이브러리 설치
pip install -r requirements.txt<br />
pip install sqlalchemy psycopg2-binary pyyaml streamlit plotly

## 6. 🚀 향후 확장 계획 (Future Work)

현재 프로젝트는 AI 기반 인프라 관리 로직을 증명하는 데 초점을 맞추었으며, 향후 실제 서비스 운영 환경으로 확장하기 위한 세 가지 주요 계획은 다음과 같습니다.

### 1. 🏋️‍♂️ 실제 헬스 서비스 기능 및 데이터 확장

현재의 가상 시나리오에서 벗어나, 실제 사용자 데이터를 처리하고 서비스 부하의 근원을 더욱 구체화합니다.

* **헬스 데이터 및 유저 데이터 추가:**
    * 사용자 신체 정보, 운동 루틴 완료 여부, 자세 교정 성공률 등의 실제 헬스 데이터를 DB 스키마에 추가합니다.
    * 이를 AI 예측의 **외부 변수 (Exogenous Variables)**로 활용하여 예측 정확도를 높입니다.
* **커뮤니티 기능 추가:**
    * '친구 초대 이벤트', '특정 챌린지 시작' 등 Keep과 같은 서비스에서 발생하는 **비정기적 이벤트**를 체계적으로 수집합니다.
    * 이벤트 데이터를 모델에 반영하여, 인프라 부하와의 상관관계를 심층 분석합니다.

---

### 2. 🧠 AutoML 도입을 통한 AI 모델 최적화

현재 Prophet 모델을 사용하고 있지만, 예측 성능을 극한으로 끌어올리기 위해 다양한 시계열 모델을 도입합니다.

* **모델 비교:**
    * Prophet 외에 **LSTM**, **Transformer 기반 모델**, 또는 **AutoGluon**과 같은 **AutoML 툴**을 사용하여 여러 모델을 자동으로 학습 및 비교합니다.
* **최적화:**
    * **MAPE**와 같은 지표를 기준으로 가장 정확한 모델을 **자동으로 선택**하고, **하이퍼파라미터 튜닝을 자동화**하여 시스템의 예측 신뢰도를 극대화합니다.

---

### 3. ☁️ 실시간 클라우드 연동 및 자동화 (Go-Live)

시뮬레이션 로직을 실제 클라우드 환경의 자동 확장 기능과 연결하여 완전한 자동 운영 시스템으로 발전시킵니다.

* **클라우드 API 연동:**
    * Python 스크립트가 CSV에 결과를 저장하는 대신, **AWS Auto Scaling Groups** 또는 **Kubernetes의 Horizontal Pod Autoscaler (HPA)** 같은 **클라우드 API**와 직접 통신하도록 수정합니다.
* **실시간 의사결정:**
    * DB 데이터를 **실시간 스트리밍**으로 처리하고 (Kafka 등), 예측 결과를 **1분 단위**로 업데이트합니다.
    * 서버 확장/축소를 즉각적으로 실행함으로써 진정한 의미의 **동적 인프라 관리**를 완성합니다.
