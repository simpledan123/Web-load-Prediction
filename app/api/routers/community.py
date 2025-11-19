from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ... import schemas, crud, database

# 라우터 설정 (URL 앞에 /users가 자동으로 붙음)
router = APIRouter(
    prefix="/users",
    tags=["Users & Workouts"]
)

# DB 세션 의존성 함수
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# [회원가입] POST /users/
@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 체크
    db_user = crud.user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.user.create_user(db=db, user=user)

# [사용자 조회] GET /users/{user_id}
@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# [운동 기록 생성] POST /users/{user_id}/workouts/
@router.post("/{user_id}/workouts/", response_model=schemas.Workout)
def create_workout(user_id: int, workout: schemas.WorkoutCreate, db: Session = Depends(get_db)):
    # 해당 유저가 존재하는지 먼저 확인하면 더 좋음
    return crud.workout.create_workout_log(db=db, workout=workout, user_id=user_id)