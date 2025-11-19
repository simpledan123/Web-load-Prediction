# 🏥 Physical AI Healthcare Platform
### : 데이터 센터의 물리적 제어를 위한 지능형 헬스케어 웹 서비스

## 📖 프로젝트 개요 (Project Overview)

본 프로젝트는 **'Keep'**과 같은 커뮤니티 기반 헬스케어 서비스에서 발생하는 **트래픽 급증(Spike)** 현상에 대응하기 위해, **Physical AI(물리적 AI)** 기술을 도입하여 데이터 센터 인프라를 효율적으로 제어하는 플랫폼입니다.

사용자에게는 **소셜 피트니스 경험**을 제공하고, 관리자에게는 **AI 기반의 인프라 자동 제어(서버 확장, 냉각, 전력 관리)** 대시보드를 제공하여 **서비스 가용성(Availability)**과 **에너지 효율성(PUE)**을 동시에 달성하는 것을 목표로 합니다.

---

## 🏗️ 시스템 아키텍처 (System Architecture)

이 프로젝트는 **Layered Architecture (계층형 아키텍처)**와 **MSA(Microservices Architecture)**의 초기 모델을 따르고 있습니다.


graph TD
    User[User Client] -->|React Frontend| FE[Web Dashboard]
    FE -->|REST API| API[FastAPI Backend]
    
    subgraph "Core Service Layer"
        API -->|ORM| DB[(PostgreSQL)]
        API -->|Prediction Request| AI["AI Engine (Prophet)"]
    end
    
    subgraph "Physical AI Operations"
        DB -->|CDC Stream| Kafka[Kafka / Spark]
        AI -->|Control Signal| Infra["AWS Auto Scaling / HVAC Control"]
    end

## 기술 스택  
Frontend,"React, Vite, Chart.js"  
Backend,Python FastAPI  
Database,PostgreSQL  
Data Ops,Alembic  
AI Model,Prophet  

## 주요 기능 (Key Features)
1. 🏃‍♂️ 사용자 모드 (Community & Workout)
기능: 사용자는 운동 기록을 저장하고, 커뮤니티 피드에 글을 작성하여 공유할 수 있습니다.

기술적 의의: 트래픽 유발원(Workload Source) 역할을 합니다. 챌린지 이벤트 발생 시 트래픽이 급증하는 시나리오를 시뮬레이션합니다.

2. 🏗️ 관리자 모드 (Physical AI Dashboard)
기능: 데이터 센터의 실시간 부하, 랙(Rack) 온도, 전력 사용량을 모니터링하고 AI의 제어 예측값을 시각화합니다.

Physical AI 제어 로직:

부하 예측: "다음 1시간 뒤 트래픽 급증 예상 -> 서버 5대 추가 증설"

물리 제어: "서버 부하 감소 -> CPU 언더클럭킹 및 냉각 팬 속도 저하 -> 전력 절감"

## 실행
## 레포지토리 클론
git clone [https://github.com/simpledan123/Web-load-Prediction.git](https://github.com/simpledan123/Web-load-Prediction.git)
cd Web-load-Prediction

## 가상환경 생성 및 활성화
conda create -n de_project python=3.10
conda activate de_project

## 백엔드 패키지 설치
pip install -r requirements.txt

# 로컬 PostgreSQL에 DB 및 유저 생성 필요 (user_health / health_db)
# Alembic을 통한 테이블 생성
alembic upgrade head

uvicorn app.main:app --reload
# Swagger 문서 접속: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

cd frontend
npm install
npm run dev
# 웹 접속: http://localhost:5173

## 추후 개발 방향
Real-time Pipeline: Kafka를 도입하여 DB의 변경 사항(CDC)을 실시간 스트리밍으로 AI 모델에 전달.

Auto Scaling 연동: 현재 시뮬레이션된 제어 로직을 AWS Boto3 또는 Kubernetes HPA와 실제로 연동.

Containerization: Docker 및 Docker Compose를 도입하여 배포 환경 통일.
