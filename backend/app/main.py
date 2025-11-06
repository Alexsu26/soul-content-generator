# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.content import router as content_router

app = FastAPI(title="Soul Content Generator API")

# CORS 配置（允许所有来源，生产环境应更严格）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "message": "Soul Content Generator API"}

# 包含内容生成的路由
app.include_router(content_router, prefix="/api", tags=["Content Generation"])
