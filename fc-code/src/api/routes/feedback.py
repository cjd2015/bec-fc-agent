"""
用户反馈接口
收集有用/无用反馈，用于质量优化
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from loguru import logger

router = APIRouter()

class FeedbackCreate(BaseModel):
    """创建反馈"""
    chunk_id: int = Field(..., description="知识片段 ID")
    feedback_type: str = Field(..., description="反馈类型：thumbs_up/thumbs_down")
    comment: Optional[str] = Field(None, description="可选评论")


class FeedbackResponse(BaseModel):
    """反馈响应"""
    id: int
    chunk_id: int
    feedback_type: str
    comment: Optional[str]
    created_at: str


@router.post("", response_model=FeedbackResponse)
async def create_feedback(feedback: FeedbackCreate):
    """
    提交用户反馈
    
    - **chunk_id**: 知识片段 ID
    - **feedback_type**: thumbs_up（有用）/ thumbs_down（无用）
    - **comment**: 可选评论
    """
    logger.info(f"💬 收到反馈：chunk_id={feedback.chunk_id}, type={feedback.feedback_type}")
    
    # TODO: 保存到数据库
    # TODO: 触发质量重新评估
    # TODO: 如果是负面反馈，检查是否需要下架
    
    return FeedbackResponse(
        id=1,
        chunk_id=feedback.chunk_id,
        feedback_type=feedback.feedback_type,
        comment=feedback.comment,
        created_at=datetime.now().isoformat()
    )


@router.get("/chunks/{chunk_id}")
async def get_chunk_feedbacks(chunk_id: int):
    """获取知识片段的反馈"""
    logger.info(f"📊 获取反馈：chunk_id={chunk_id}")
    
    # TODO: 从数据库查询
    
    return {
        "chunk_id": chunk_id,
        "total": 0,
        "thumbs_up": 0,
        "thumbs_down": 0,
        "feedbacks": []
    }


@router.get("/stats")
async def get_feedback_stats():
    """获取反馈统计"""
    logger.info("📊 获取反馈统计")
    
    # TODO: 实现统计
    
    return {
        "total_feedbacks": 0,
        "thumbs_up": 0,
        "thumbs_down": 0,
        "positive_rate": 0.0,
        "recent_trend": []
    }
