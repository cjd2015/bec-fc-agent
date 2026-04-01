"""
AI Agent Platform - FastAPI 入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from .routes import health, chat, memory, knowledge, task, feedback, metrics, agent
from .middleware.logging import setup_logging

# 创建 FastAPI 应用
app = FastAPI(
    title="AI Agent Platform",
    description="基于 Python 的 AI Agent 平台，支持多模型接入、知识库 RAG、任务编排",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 设置日志
setup_logging()

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, tags=["健康检查"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["对话"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["记忆管理"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["知识库"])
app.include_router(task.router, prefix="/api/v1/task", tags=["任务管理"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["用户反馈"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["质量监控"])
app.include_router(agent.router, prefix="/api/v1/agent", tags=["BEC Agent"])

# 生命周期事件
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 AI Agent Platform 启动中...")
    logger.info(f"📦 版本：{app.title} v{app.version}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 AI Agent Platform 关闭")

# 根路径
@app.get("/")
async def root():
    return {
        "name": "AI Agent Platform",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
