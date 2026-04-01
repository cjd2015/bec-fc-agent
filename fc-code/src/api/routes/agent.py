"""
BEC Agent 管理接口
支持 CRUD、版本控制、操作日志和回滚
"""
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
import json
from copy import deepcopy

from src.utils.database import get_async_session, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.models.agent import Agent, AgentVersion, AgentOperationLog, AgentStatus, OperationType
from src.models.knowledge import KnowledgeBase

router = APIRouter()


# ==================== 请求/响应模型 ====================

class AgentCreate(BaseModel):
    """创建 Agent 请求"""
    name: str = Field(..., description="Agent 名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="描述")
    icon: Optional[str] = Field(None, description="图标 URL")
    
    # 模型配置
    provider: str = Field(default="novacode", description="Provider")
    model: str = Field(default="codex-mini-latest", description="模型 ID")
    model_variant: str = Field(default="medium", description="模型变体")
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=4096, ge=100, le=128000)
    
    # 系统提示词
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    
    # 知识库关联
    knowledge_base_ids: List[int] = Field(default_factory=list, description="知识库 ID 列表")


class AgentUpdate(BaseModel):
    """更新 Agent 请求"""
    name: Optional[str] = Field(None, description="Agent 名称")
    description: Optional[str] = Field(None, description="描述")
    icon: Optional[str] = Field(None, description="图标 URL")
    
    # 模型配置
    provider: Optional[str] = Field(None, description="Provider")
    model: Optional[str] = Field(None, description="模型 ID")
    model_variant: Optional[str] = Field(None, description="模型变体")
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, ge=100, le=128000)
    
    # 系统提示词
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    
    # 知识库关联
    knowledge_base_ids: Optional[List[int]] = Field(None, description="知识库 ID 列表")
    
    # 是否创建新版本（用于回滚）
    create_version: bool = Field(default=True, description="是否创建版本快照")
    change_summary: Optional[str] = Field(None, description="变更摘要")


class AgentResponse(BaseModel):
    """Agent 响应"""
    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    provider: str
    model: str
    model_variant: str
    temperature: float
    max_tokens: int
    system_prompt: Optional[str]
    knowledge_base_ids: List[int]
    status: str
    version: int
    total_conversations: int
    total_messages: int
    avg_rating: float
    created_at: str
    updated_at: str


class AgentVersionResponse(BaseModel):
    """Agent 版本响应"""
    id: int
    agent_id: int
    version: int
    change_summary: Optional[str]
    change_details: Optional[Dict]
    operator_name: Optional[str]
    created_at: str
    is_rollback_target: bool


class AgentOperationLogResponse(BaseModel):
    """操作日志响应"""
    id: int
    agent_id: int
    operation_type: str
    operation_name: str
    operator_name: Optional[str]
    status: str
    can_rollback: bool
    created_at: str


# ==================== 辅助函数 ====================

async def get_agent_or_404(db: AsyncSession, agent_id: int) -> Agent:
    """获取 Agent 或抛出 404"""
    result = await db.execute(select(Agent).where(Agent.id == agent_id, Agent.is_deleted == False))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent 不存在")
    return agent


def get_snapshot(agent: Agent) -> Dict:
    """获取 Agent 快照"""
    return {
        "name": agent.name,
        "description": agent.description,
        "icon": agent.icon,
        "provider": agent.provider,
        "model": agent.model,
        "model_variant": agent.model_variant,
        "temperature": agent.temperature,
        "max_tokens": agent.max_tokens,
        "system_prompt": agent.system_prompt,
        "knowledge_base_ids": agent.knowledge_base_ids,
        "status": agent.status,
        "version": agent.version
    }


def diff_snapshots(before: Dict, after: Dict) -> Dict:
    """比较两个快照的差异"""
    changes = {}
    for key in set(list(before.keys()) + list(after.keys())):
        if before.get(key) != after.get(key):
            changes[key] = {
                "old": before.get(key),
                "new": after.get(key)
            }
    return changes


async def create_version(db: AsyncSession, agent: Agent, operator_id: int = None, 
                         change_summary: str = None) -> AgentVersion:
    """创建版本快照"""
    snapshot = get_snapshot(agent)
    
    version = AgentVersion(
        agent_id=agent.id,
        version=agent.version,
        snapshot=snapshot,
        change_summary=change_summary,
        operator_id=operator_id
    )
    
    db.add(version)
    await db.flush()
    
    # 更新 agent 的 current_version_id
    agent.current_version_id = version.id
    
    return version


async def log_operation(db: AsyncSession, agent: Agent, operation_type: OperationType,
                       before_snapshot: Dict = None, after_snapshot: Dict = None,
                       operator_id: int = None, operator_name: str = None,
                       request: Request = None, error_message: str = None) -> AgentOperationLog:
    """记录操作日志"""
    changes = None
    if before_snapshot and after_snapshot:
        changes = diff_snapshots(before_snapshot, after_snapshot)
    
    log = AgentOperationLog(
        agent_id=agent.id,
        operation_type=operation_type.value,
        operation_name=f"{operation_type.value}_agent",
        before_snapshot=before_snapshot,
        after_snapshot=after_snapshot,
        changes=changes,
        operator_id=operator_id,
        operator_name=operator_name,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
        status="success" if not error_message else "failed",
        error_message=error_message,
        can_rollback=operation_type in [OperationType.UPDATE, OperationType.DELETE, OperationType.ROLLBACK]
    )
    
    db.add(log)
    return log


# ==================== API 接口 ====================

@router.post("", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_async_session),
    request: Request = None
):
    """
    创建新的 Agent
    
    - **name**: Agent 名称（必填）
    - **description**: 描述
    - **provider**: Provider 名称
    - **model**: 模型 ID
    - **knowledge_base_ids**: 关联的知识库 ID 列表
    """
    logger.info(f"🤖 创建 Agent: {agent_data.name}")
    
    try:
        # 创建 Agent
        agent = Agent(
            name=agent_data.name,
            description=agent_data.description,
            icon=agent_data.icon,
            provider=agent_data.provider,
            model=agent_data.model,
            model_variant=agent_data.model_variant,
            temperature=agent_data.temperature,
            max_tokens=agent_data.max_tokens,
            system_prompt=agent_data.system_prompt,
            knowledge_base_ids=agent_data.knowledge_base_ids,
            status=AgentStatus.DRAFT.value,
            version=1
        )
        
        db.add(agent)
        await db.flush()  # 获取 agent.id
        
        # 创建初始版本
        await create_version(db, agent, change_summary="创建初始版本")
        
        # 记录操作日志
        after_snapshot = get_snapshot(agent)
        await log_operation(
            db, agent, OperationType.CREATE,
            after_snapshot=after_snapshot,
            request=request
        )
        
        await db.commit()
        await db.refresh(agent)
        
        logger.info(f"✅ Agent 创建成功：id={agent.id}")
        
        return agent
    
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Agent 创建失败：{e}")
        raise HTTPException(status_code=500, detail=f"创建失败：{str(e)}")


@router.get("", response_model=List[AgentResponse])
async def list_agents(
    status: Optional[str] = Query(None, description="状态过滤"),
    limit: int = Query(50, description="返回数量", ge=1, le=200),
    offset: int = Query(0, description="偏移量", ge=0),
    db: AsyncSession = Depends(get_async_session)
):
    """获取 Agent 列表"""
    logger.info(f"📋 获取 Agent 列表：status={status}, limit={limit}")
    
    query = select(Agent).where(Agent.is_deleted == False)
    
    if status:
        query = query.where(Agent.status == status)
    
    query = query.order_by(Agent.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    agents = result.scalars().all()
    
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """获取 Agent 详情"""
    logger.info(f"📖 获取 Agent 详情：id={agent_id}")
    
    agent = await get_agent_or_404(db, agent_id)
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_async_session),
    request: Request = None
):
    """
    更新 Agent
    
    - **create_version**: 是否创建版本快照（默认 True，用于回滚）
    - **change_summary**: 变更摘要
    """
    logger.info(f"✏️ 更新 Agent: id={agent_id}")
    
    try:
        agent = await get_agent_or_404(db, agent_id)
        
        # 保存操作前快照
        before_snapshot = get_snapshot(agent)
        
        # 如果创建新版本，先保存当前版本
        if agent_data.create_version:
            await create_version(
                db, agent,
                change_summary=agent_data.change_summary or "更新配置"
            )
        
        # 更新字段
        update_data = agent_data.model_dump(exclude_unset=True, exclude={"create_version", "change_summary"})
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        # 版本号 +1
        agent.version += 1
        agent.updated_at = datetime.now()
        
        # 保存操作后快照
        after_snapshot = get_snapshot(agent)
        
        # 创建新版本（如果更新后还需要保存）
        if agent_data.create_version:
            await create_version(
                db, agent,
                change_summary=agent_data.change_summary or "更新配置"
            )
        
        # 记录操作日志
        await log_operation(
            db, agent, OperationType.UPDATE,
            before_snapshot=before_snapshot,
            after_snapshot=after_snapshot,
            request=request
        )
        
        await db.commit()
        await db.refresh(agent)
        
        logger.info(f"✅ Agent 更新成功：id={agent_id}, version={agent.version}")
        
        return agent
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Agent 更新失败：{e}")
        raise HTTPException(status_code=500, detail=f"更新失败：{str(e)}")


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_async_session),
    request: Request = None
):
    """
    删除 Agent（软删除，可恢复）
    
    标记为已删除，但保留数据以便恢复
    """
    logger.info(f"🗑️ 删除 Agent: id={agent_id}")
    
    try:
        agent = await get_agent_or_404(db, agent_id)
        
        # 保存操作前快照
        before_snapshot = get_snapshot(agent)
        
        # 软删除
        agent.is_deleted = True
        agent.status = AgentStatus.ARCHIVED.value
        agent.updated_at = datetime.now()
        
        # 记录操作日志
        await log_operation(
            db, agent, OperationType.DELETE,
            before_snapshot=before_snapshot,
            request=request
        )
        
        await db.commit()
        
        logger.info(f"✅ Agent 删除成功：id={agent_id}")
        
        return {"status": "ok", "message": f"Agent {agent_id} 已删除（可恢复）"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Agent 删除失败：{e}")
        raise HTTPException(status_code=500, detail=f"删除失败：{str(e)}")


@router.post("/{agent_id}/restore")
async def restore_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_async_session),
    request: Request = None
):
    """恢复已删除的 Agent"""
    logger.info(f"♻️ 恢复 Agent: id={agent_id}")
    
    # 查询已删除的 Agent
    result = await db.execute(select(Agent).where(Agent.id == agent_id, Agent.is_deleted == True))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent 不存在或未被删除")
    
    try:
        before_snapshot = get_snapshot(agent)
        
        # 恢复
        agent.is_deleted = False
        agent.status = AgentStatus.DRAFT.value
        agent.updated_at = datetime.now()
        
        after_snapshot = get_snapshot(agent)
        
        # 记录操作日志
        await log_operation(
            db, agent, OperationType.ROLLBACK,
            before_snapshot=before_snapshot,
            after_snapshot=after_snapshot,
            operation_name="restore_agent",
            request=request
        )
        
        await db.commit()
        
        logger.info(f"✅ Agent 恢复成功：id={agent_id}")
        
        return {"status": "ok", "message": f"Agent {agent_id} 已恢复"}
    
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Agent 恢复失败：{e}")
        raise HTTPException(status_code=500, detail=f"恢复失败：{str(e)}")


@router.get("/{agent_id}/versions", response_model=List[AgentVersionResponse])
async def list_agent_versions(
    agent_id: int,
    limit: int = Query(50, description="返回数量", ge=1, le=200),
    db: AsyncSession = Depends(get_async_session)
):
    """获取 Agent 版本历史"""
    logger.info(f"📜 获取 Agent 版本历史：id={agent_id}")
    
    query = (
        select(AgentVersion)
        .where(AgentVersion.agent_id == agent_id)
        .order_by(AgentVersion.version.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    versions = result.scalars().all()
    
    return versions


@router.get("/{agent_id}/versions/{version_id}")
async def get_agent_version(
    agent_id: int,
    version_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """获取特定版本详情"""
    logger.info(f"📖 获取版本详情：agent_id={agent_id}, version_id={version_id}")
    
    result = await db.execute(
        select(AgentVersion).where(
            AgentVersion.id == version_id,
            AgentVersion.agent_id == agent_id
        )
    )
    version = result.scalar_one_or_none()
    
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    return {
        "id": version.id,
        "agent_id": version.agent_id,
        "version": version.version,
        "snapshot": version.snapshot,
        "change_summary": version.change_summary,
        "change_details": version.change_details,
        "created_at": version.created_at.isoformat()
    }


@router.post("/{agent_id}/rollback/{version_id}")
async def rollback_to_version(
    agent_id: int,
    version_id: int,
    db: AsyncSession = Depends(get_async_session),
    request: Request = None
):
    """
    回滚到指定版本
    
    会创建一个新的版本记录当前状态，然后恢复到目标版本
    """
    logger.info(f"🔙 回滚 Agent: id={agent_id}, target_version={version_id}")
    
    try:
        agent = await get_agent_or_404(db, agent_id)
        
        # 获取目标版本
        result = await db.execute(
            select(AgentVersion).where(
                AgentVersion.id == version_id,
                AgentVersion.agent_id == agent_id
            )
        )
        target_version = result.scalar_one_or_none()
        
        if not target_version:
            raise HTTPException(status_code=404, detail="目标版本不存在")
        
        # 保存当前状态
        before_snapshot = get_snapshot(agent)
        
        # 创建当前版本快照
        await create_version(
            db, agent,
            change_summary=f"回滚前备份 (当前版本 v{agent.version})"
        )
        
        # 恢复到目标版本
        snapshot = target_version.snapshot
        agent.name = snapshot["name"]
        agent.description = snapshot.get("description")
        agent.icon = snapshot.get("icon")
        agent.provider = snapshot.get("provider", "novacode")
        agent.model = snapshot.get("model", "codex-mini-latest")
        agent.model_variant = snapshot.get("model_variant", "medium")
        agent.temperature = snapshot.get("temperature", 0.7)
        agent.max_tokens = snapshot.get("max_tokens", 4096)
        agent.system_prompt = snapshot.get("system_prompt")
        agent.knowledge_base_ids = snapshot.get("knowledge_base_ids", [])
        
        # 版本号 +1
        agent.version += 1
        agent.updated_at = datetime.now()
        
        # 保存恢复后的快照
        after_snapshot = get_snapshot(agent)
        
        # 创建新版本
        await create_version(
            db, agent,
            change_summary=f"回滚到版本 v{target_version.version}"
        )
        
        # 记录操作日志
        await log_operation(
            db, agent, OperationType.ROLLBACK,
            before_snapshot=before_snapshot,
            after_snapshot=after_snapshot,
            change_details={"target_version_id": version_id, "target_version": target_version.version},
            request=request
        )
        
        await db.commit()
        await db.refresh(agent)
        
        logger.info(f"✅ Agent 回滚成功：id={agent_id}, 回滚到版本 v{target_version.version}")
        
        return {
            "status": "ok",
            "message": f"已回滚到版本 v{target_version.version}",
            "current_version": agent.version
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Agent 回滚失败：{e}")
        raise HTTPException(status_code=500, detail=f"回滚失败：{str(e)}")


@router.get("/{agent_id}/operations", response_model=List[AgentOperationLogResponse])
async def list_agent_operations(
    agent_id: int,
    limit: int = Query(50, description="返回数量", ge=1, le=200),
    db: AsyncSession = Depends(get_async_session)
):
    """获取 Agent 操作日志"""
    logger.info(f"📋 获取 Agent 操作日志：id={agent_id}")
    
    query = (
        select(AgentOperationLog)
        .where(AgentOperationLog.agent_id == agent_id)
        .order_by(AgentOperationLog.created_at.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    operations = result.scalars().all()
    
    return operations


@router.get("/{agent_id}/operations/{operation_id}")
async def get_operation_detail(
    agent_id: int,
    operation_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """获取操作详情（包含变更内容）"""
    logger.info(f"📖 获取操作详情：operation_id={operation_id}")
    
    result = await db.execute(
        select(AgentOperationLog).where(
            AgentOperationLog.id == operation_id,
            AgentOperationLog.agent_id == agent_id
        )
    )
    operation = result.scalar_one_or_none()
    
    if not operation:
        raise HTTPException(status_code=404, detail="操作记录不存在")
    
    return {
        "id": operation.id,
        "agent_id": operation.agent_id,
        "operation_type": operation.operation_type,
        "operation_name": operation.operation_name,
        "before_snapshot": operation.before_snapshot,
        "after_snapshot": operation.after_snapshot,
        "changes": operation.changes,
        "operator_name": operation.operator_name,
        "ip_address": operation.ip_address,
        "status": operation.status,
        "error_message": operation.error_message,
        "can_rollback": operation.can_rollback,
        "created_at": operation.created_at.isoformat()
    }
