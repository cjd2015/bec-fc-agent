"""
任务模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.utils.database import Base


class Task(Base):
    """任务表"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # 任务信息
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # 工作流定义
    workflow = Column(JSON, nullable=False)
    
    # 触发器配置
    trigger_type = Column(String(20), default="manual")  # manual/cron/event
    trigger_config = Column(JSON)  # cron 表达式或事件配置
    
    # 状态
    status = Column(String(20), default="pending")  # pending/running/completed/failed
    enabled = Column(Boolean, default=True)
    
    # 执行信息
    last_run = Column(DateTime(timezone=True))
    next_run = Column(DateTime(timezone=True))
    last_run_status = Column(String(20))
    last_error = Column(Text)
    
    # 统计
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联
    user = relationship("User", backref="tasks")
    runs = relationship("TaskRun", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task(id={self.id}, name={self.name})>"


class TaskRun(Base):
    """任务执行记录表"""
    __tablename__ = "task_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), index=True)
    
    # 执行信息
    run_id = Column(String(64), unique=True, index=True)
    status = Column(String(20), default="running")  # running/completed/failed
    
    # 时间
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # 结果
    result = Column(JSON)
    error_message = Column(Text)
    
    # 关联
    task = relationship("Task", back_populates="runs")
    
    def __repr__(self):
        return f"<TaskRun(id={self.id}, status={self.status})>"
