from fastapi import FastAPI
# CORS 설정 (프론트엔드 포트 3000, 5173 등 허용)
origins = [
    "http://localhost:3000", # React 기본 포트
    "http://localhost:5173", # Vite(React) 기본 포트
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi.middleware.cors import CORSMiddleware

# 우리가 만든 라우터들 import
from .api.routers import users, community, infra

app = FastAPI(
    title="Physical AI Healthcare Platform",
    description="Modular Backend with Physical AI & Community Features",
    version="1.0.0"
)

# 라우터 등록 (조립)
app.include_router(users.router)
app.include_router(community.router)
app.include_router(infra.router)

@app.get("/")
def root():
    return {"message": "Physical AI Healthcare Server is Running! 🚀"}