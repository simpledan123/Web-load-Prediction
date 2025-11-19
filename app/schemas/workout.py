from pydantic import BaseModel
from datetime import datetime

# [기본] 공통적으로 사용되는 필드
class WorkoutBase(BaseModel):
    activity_type: str
    duration_minutes: int
    calories_burned: float

# [생성] 사용자가 운동을 기록할 때 (기본 필드와 동일)
class WorkoutCreate(WorkoutBase):
    pass

# [응답] DB에서 꺼내서 사용자에게 보여줄 때 (ID, 시간 포함)
class Workout(WorkoutBase):
    id: int
    user_id: int
    logged_at: datetime

    # ORM(SQLAlchemy) 객체를 Pydantic 모델로 읽기 위해 필수 설정
    class Config:
        from_attributes = True