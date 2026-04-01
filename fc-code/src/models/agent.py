"""
BEC Agent 模型
支持 CRUD 操作、版本控制和操作日志
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.utils.database import Base
from enum import Enum as PyEnum


class AgentStatus(str, PyEnum):
    """Agent 状态"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 激活
    INACTIVE = "inactive"  # 停用
    ARCHIVED = "archived"  # 归档


class OperationType(str, PyEnum):
    """操作类型"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ROLLBACK = "rollback"
    PUBLISH = "publish"


class Agent(Base):
    """BEC Agent 主表"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # 基本信息
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    icon = Column(String(500))  # 图标 URL
    
    # 配置
    provider = Column(String(50), default="novacode")
    model = Column(String(100), default="codex-mini-latest")
    model_variant = Column(String(20), default="medium")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=4096)
    
    # 系统提示词
    system_prompt = Column(Text)
    
    # 知识库关联
    knowledge_base_ids = Column(JSON, default=list)  # [kb_id1, kb_id2]
    
    # 状态
    status = Column(String(20), default=AgentStatus.DRAFT.value)
    version = Column(Integer, default=1)  # 当前版本号
    
    # 统计
    total_conversations = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    avg_rating = Column(Float, default=0.0)
    
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联
    user = relationship("User", backref="agents")
    versions = relationship("AgentVersion", primaryjoin="Agent.id == AgentVersion.agent_id", back_populates="agent", cascade="all, delete-orphan", foreign_keys="AgentVersion.agent_id")
    operations = relationship("AgentOperationLog", primaryjoin="Agent.id == AgentOperationLog.agent_id", back_populates="agent", cascade="all, delete-orphan", foreign_keys="AgentOperationLog.agent_id")
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, version={self.version})>"


class AgentVersion(Base):
    """Agent 版本表（用于回滚）"""
    __tablename__ = "agent_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), index=True, nullable=False)
    version = Column(Integer, nullable=False)  # 版本号
    
    # 版本快照（完整配置）
    snapshot = Column(JSON, nullable=False)
    
    # 版本信息
    change_summary = Column(String(500))  # 变更摘要
    change_details = Column(JSON)  # 详细变更
    
    # 操作者
    operator_id = Column(Integer, ForeignKey("users.id"))
    
    # 是否可以回滚到此版本
    is_rollback_target = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联
    agent = relationship("Agent", primaryjoin="AgentVersion.agent_id == Agent.id", back_populates="versions", foreign_keys="AgentVersion.agent_id")
    
    __table_args__ = (
        # 唯一约束：同一个 agent 的同一个版本只能有一条记录
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<AgentVersion(agent_id={self.agent_id}, version={self.version})>"


class AgentOperationLog(Base):
    """Agent 操作日志表（审计追踪）"""
    __tablename__ = "agent_operation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), index=True, nullable=False)
    
    # 操作信息
    operation_type = Column(String(20), nullable=False)  # create/update/delete/rollback/publish
    operation_name = Column(String(100))  # 操作名称
    
    # 操作前后快照
    before_snapshot = Column(JSON)  # 操作前状态
    after_snapshot = Column(JSON)  # 操作后状态
    
    # 变更详情
    changes = Column(JSON)  # 具体变更字段
    
    # 操作者
    operator_id = Column(Integer, ForeignKey("users.id"))
    operator_name = Column(String(50))
    
    # IP 和设备
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # 结果
    status = Column(String(20), default="success")  # success/failed
    error_message = Column(Text)
    
    # 是否可以回滚
    can_rollback = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联
    agent = relationship("Agent", back_populates="operations")
    
    def __repr__(self):
        return f"<AgentOperationLog(id={self.id}, type={self.operation_type})>"


class AgentKnowledgeLink(Base):
    """Agent 与知识库关联表"""
    __tablename__ = "agent_knowledge_links"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), index=True, nullable=False)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), index=True, nullable=False)
    
    # 关联配置
    search_weight = Column(Float, default=1.0)  # 检索权重
    max_chunks = Column(Integer, default=10)  # 最大返回片段数
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        # 唯一约束
        {'sqlite_autoincrement': True}
    )
