# 数据库 Docker 部署与低配参数建议

**版本:** 1.0  
**更新日期:** 2026-03-31

## 1. 部署目标
在当前 ECS（2核2G）上使用 Docker 运行 PostgreSQL 或 MySQL，支撑 MVP 阶段业务。

## 2. 推荐选择
### 优先推荐
- PostgreSQL

### 原因
- 更适合复杂结构化建模
- 更适合后续扩展
- 对 BEC 项目数据表设计更友好

## 3. Docker 部署原则
- 单独 volume 持久化
- 限制容器资源
- 配置自动重启
- 控制日志大小
- 避免默认参数直接运行

## 4. PostgreSQL Docker 示例
```yaml
version: "3.9"

services:
  postgres:
    image: postgres:16
    container_name: bec-postgres
    restart: always
    environment:
      POSTGRES_DB: bec_agent
      POSTGRES_USER: bec_user
      POSTGRES_PASSWORD: your_strong_password
    ports:
      - "5432:5432"
    volumes:
      - ./postgres-data:/var/lib/postgresql/data
      - ./postgresql.conf:/etc/postgresql/postgresql.conf
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
```

## 5. PostgreSQL 低配参数建议
```conf
max_connections = 30
shared_buffers = 128MB
work_mem = 4MB
maintenance_work_mem = 32MB
effective_cache_size = 512MB
wal_buffers = 4MB
checkpoint_completion_target = 0.7
random_page_cost = 1.1
log_min_duration_statement = 1000
```

## 6. MySQL 低配参数建议
```conf
[mysqld]
max_connections=30
innodb_buffer_pool_size=256M
innodb_log_buffer_size=16M
table_open_cache=128
thread_cache_size=8
tmp_table_size=16M
max_heap_table_size=16M
```

## 7. 运行注意事项
- 不要开放默认弱口令
- 不要把数据库完全裸暴露公网
- 控制最大连接数
- 定期清理日志和备份
- 避免复杂长事务和大查询
