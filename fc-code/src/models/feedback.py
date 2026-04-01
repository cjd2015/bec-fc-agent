"""
用户反馈模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.utils.database import Base


class Feedback(Base):
    """用户反馈表"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # 反馈对象
    chunk_id = Column(Integer, ForeignKey("knowledge_chunks.id"), index=True)
    
    # 反馈内容
    feedback_type = Column(String(20), nullable=False)  # thumbs_up/thumbs_down
    comment = Column(Text)
    
    # 处理状态
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联
    user = relationship("User", backref="feedbacks")
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, type={self.feedback_type})>"
