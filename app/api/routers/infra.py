from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ... import database, models

router = APIRouter(
    prefix="/infra",
    tags=["Physical AI Infrastructure"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# [인프라 상태 조회] GET /infra/status
@router.get("/status")
def get_infra_status(db: Session = Depends(get_db)):
    """
    현재 DB에 쌓인 데이터 양을 기반으로 인프라 부하 상태를 계산하여 반환합니다.
    (추후 Kafka 실시간 데이터와 연동될 지점)
    """
    user_count = db.query(models.User).count()
    post_count = db.query(models.CommunityPost).count()
    
    # 단순 시뮬레이션 로직
    load_status = "Stable"
    predicted_servers = 3
    
    if post_count > 100:
        load_status = "High Load (Traffic Spike Detected)"
        predicted_servers = 8
    
    return {
        "active_users": user_count,
        "total_posts": post_count,
        "system_status": load_status,
        "ai_prediction": {
            "needed_servers": predicted_servers,
            "rack_temperature_avg": 24.5,  # 가상 센서 데이터
            "power_usage_watt": 1200
        }
    }