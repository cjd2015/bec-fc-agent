"""
数据库管理模块
支持 SQLite（单机）和 PostgreSQL（扩展）
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from sqlalchemy import text
from loguru import logger
from typing import Optional

# 基础类
Base = declarative_base()

# 全局变量
_engine = None
_async_session_factory = None
_sync_session_factory = None


def get_database_url() -> str:
    """获取数据库 URL"""
    url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/agent.db")
    
    # SQLite 优化
    if url.startswith("sqlite"):
        # 确保 data 目录存在
        os.makedirs("data", exist_ok=True)
    
    return url


def init_engine():
    """初始化数据库引擎"""
    global _engine, _async_session_factory, _sync_session_factory
    
    database_url = get_database_url()
    logger.info(f"📊 初始化数据库：{database_url}")
    
    if database_url.startswith("sqlite"):
        # SQLite 配置
        _engine = create_async_engine(
            database_url,
            echo=False,
            connect_args={
                "timeout": 30,
                "check_same_thread": False
            },
            pool_pre_ping=True
        )
        
        # SQLite 优化
        async def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.close()
        
        from sqlalchemy import event
        event.listen(_engine.sync_engine, "connect", set_sqlite_pragma)
    
    elif database_url.startswith("postgresql"):
        # PostgreSQL 配置
        _engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=20,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True
        )
    
    else:
        raise ValueError(f"不支持的数据库类型：{database_url}")
    
    # 创建会话工厂
    _async_session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    _sync_session_factory = sessionmaker(
        _engine.sync_engine,
        class_=Session,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    logger.info("✅ 数据库初始化完成")


async def create_tables():
    """创建所有表"""
    logger.info("📋 创建数据库表...")
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 验证
    async with get_async_session() as session:
        result = await session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = result.fetchall()
        logger.info(f"✅ 已创建 {len(tables)} 个表：{[t[0] for t in tables]}")
    
    logger.info("✅ 数据库表创建完成")


async def drop_tables():
    """删除所有表（慎用！）"""
    logger.warning("⚠️ 删除所有数据库表...")
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    logger.warning("✅ 数据库表已删除")


def get_async_session() -> AsyncSession:
    """获取异步会话"""
    if not _async_session_factory:
        init_engine()
    
    return _async_session_factory()


def get_sync_session() -> Session:
    """获取同步会话"""
    if not _sync_session_factory:
        init_engine()
    
    return _sync_session_factory()


async def check_health() -> dict:
    """检查数据库健康状态"""
    try:
        async with _async_session_factory() as session:
            # 测试查询
            await session.execute(text("SELECT 1"))
            
            # 获取表数量
            if get_database_url().startswith("sqlite"):
                result = await session.execute(
                    text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                )
            else:
                result = await session.execute(
                    text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'")
                )
            
            table_count = result.scalar()
            
            return {
                "status": "ok",
                "database": get_database_url().split(":")[0],
                "tables": table_count
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# 便捷函数
async def get_db() -> AsyncSession:
    """依赖注入：获取数据库会话"""
    async with get_async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# 初始化（延迟到第一次使用时）
# init_engine()
