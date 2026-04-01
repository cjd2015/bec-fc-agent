"""
知识库模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.utils.database import Base


class KnowledgeBase(Base):
    """知识库表"""
    __tablename__ = "knowledge_bases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(String(20), default="document")  # document/web/database
    
    # 统计
    chunk_count = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    avg_quality_score = Column(Float, default=0.0)
    
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联
    user = relationship("User", backref="knowledge_bases")
    chunks = relationship("KnowledgeChunk", back_populates="knowledge_base", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, name={self.name})>"


class KnowledgeChunk(Base):
    """知识片段表"""
    __tablename__ = "knowledge_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), index=True)
    
    # 内容
    content = Column(Text, nullable=False)
    title = Column(String(200))
    source = Column(String(500))  # 来源（文件路径/URL）
    page_number = Column(Integer)  # 页码（PDF）
    
    # 元数据
    meta_data = Column(JSON, default=dict)  # 改名避免冲突
    tags = Column(JSON, default=list)
    tokens = Column(Integer, default=0)
    
    # 质量评分
    quality_score = Column(Float, default=0.0)
    quality_dimensions = Column(JSON)  # 各维度评分
    auto_pass = Column(Boolean, default=False)
    needs_review = Column(Boolean, default=False)
    
    # 向量嵌入
    embedding = Column(JSON)  # 存储向量数据
    
    # 统计
    thumbs_up = Column(Integer, default=0)
    thumbs_down = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联
    knowledge_base = relationship("KnowledgeBase", back_populates="chunks")
    
    def __repr__(self):
        return f"<KnowledgeChunk(id={self.id}, title={self.title})>"


class CrawlTask(Base):
    """爬虫任务表"""
    __tablename__ = "crawl_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), index=True)
    
    # 任务配置
    urls = Column(JSON, nullable=False)
    crawler_name = Column(String(50), default="default")
    max_depth = Column(Integer, default=2)
    follow_links = Column(Boolean, default=False)
    
    # 状态
    status = Column(String(20), default="pending")  # pending/running/completed/failed
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text)
    
    # 结果
    pages_crawled = Column(Integer, default=0)
    chunks_created = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<CrawlTask(id={self.id}, status={self.status})>"
