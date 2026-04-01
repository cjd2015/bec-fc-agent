"""
记忆模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.utils.database import Base


class Memory(Base):
    """记忆表（长期记忆）"""
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    conversation_id = Column(String(64), index=True)
    
    # 消息内容
    user_message = Column(Text, nullable=False)
    assistant_message = Column(Text, nullable=False)
    
    # 元数据
    tags = Column(JSON, default=list)
    tokens = Column(Integer, default=0)
    
    # 向量嵌入（用于语义搜索）
    embedding = Column(JSON)  # 存储向量数据
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联
    user = relationship("User", backref="memories")
    
    def __repr__(self):
        return f"<Memory(id={self.id}, conversation_id={self.conversation_id})>"


class Conversation(Base):
    """会话表"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String(200))
    provider = Column(String(50))  # 使用的 Provider
    model = Column(String(100))    # 使用的模型
    
    # 统计
    message_count = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联
    user = relationship("User", backref="conversations")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title})>"
