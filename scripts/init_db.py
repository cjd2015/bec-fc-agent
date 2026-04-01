#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.database import init_engine, create_tables, get_async_session
from sqlalchemy import text


async def main():
    """主函数"""
    print("🚀 初始化数据库...")
    
    # 初始化引擎
    init_engine()
    
    # 创建表
    await create_tables()
    
    # 显示表列表
    async with get_async_session() as session:
        result = await session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        )
        tables = [row[0] for row in result.fetchall()]
        
        print(f"\n✅ 数据库初始化完成!")
        print(f"\n📋 表列表 ({len(tables)} 个):")
        for table in tables:
            print(f"   ✓ {table}")


if __name__ == "__main__":
    asyncio.run(main())
