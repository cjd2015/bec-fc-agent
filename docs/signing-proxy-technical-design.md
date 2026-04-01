# Python 签名代理服务技术设计

**版本:** 1.0  
**更新时间:** 2026-03-31

---

## 1. 目标

为适配阿里云 FC `function` 认证模式，在 ECS 上增加一个轻量 Python 签名代理服务，负责：
- 接收 Nginx 转发的 `/api/` 请求
- 使用服务端保存的 AK/SK 对 FC 请求进行签名
- 转发请求到 FC
- 回传响应给浏览器

---

## 2. 推荐链路

```text
Browser
  -> https://datahive.top/api/
  -> ECS Nginx
  -> 127.0.0.1:9000
  -> Python Signing Proxy
  -> FC(Function Auth)
```

---

## 3. 技术选型

- Python 3.10+
- FastAPI
- httpx
- systemd（正式部署时）

---

## 4. 当前项目结构

```text
signing-proxy/
├── app/
│   └── main.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 5. 当前状态说明

当前已完成：
- 服务骨架
- 健康检查
- 请求转发结构
- 环境变量模板
- Function Auth 基础签名逻辑
- Date / Authorization / Content-MD5 头生成

当前未完成：
- 更完整的签名兼容性校验
- 日志审计
- 错误码映射
- 重试机制
- 生产部署脚本

---

## 6. 后续建议

建议下一步继续补：
1. FC Function Auth 签名实现
2. systemd 服务文件
3. 部署 runbook
4. 联调检查项
