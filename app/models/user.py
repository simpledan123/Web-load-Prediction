from fastapi import FastAPI
from .database import engine
from .models import Base  # models/__init__.py 덕분에 이렇게 import 가능
from .api.routers import users, community # 라우터 모듈 import

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Keep-Style Healthcare Platform",
    description="Modular Structure Applied"
)

# 라우터 등록 (이 한 줄로 users.py의 모든 API가 연결됨)
app.include_router(users.router)
# app.include_router(community.router) # 커뮤니티 라우터도 만들어서 연결

@app.get("/")
def root():
    return {"message": "Server is running with modular structure!"}