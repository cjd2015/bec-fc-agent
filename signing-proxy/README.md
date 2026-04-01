# BEC FC Signing Proxy

这是一个部署在 ECS 本机的轻量 Python 代理服务，用于承接：

- 浏览器 -> `https://datahive.top/api/`
- ECS Nginx -> `127.0.0.1:9000`
- Proxy -> 阿里云 FC(Function Auth)

## 当前状态
当前版本已完成：
- FastAPI 服务入口
- `/health` 健康检查
- 通用 API 转发结构
- 阿里云 FC Function Auth 基础签名逻辑
- 基础环境变量模板

当前仍建议继续补充：
- 更完整的 Canonical 规则校验
- 重试逻辑
- 审计日志
- systemd 部署文件
- 更细的错误码映射

## 本地启动
```bash
cd signing-proxy
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FC_BASE_URL="https://bec-agent-api-yelolrsptv.cn-hangzhou.fcapp.run"
export ALIYUN_ACCESS_KEY_ID="your_ak"
export ALIYUN_ACCESS_KEY_SECRET="your_sk"
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

## 健康检查
```bash
curl http://127.0.0.1:9000/health
```

## Nginx 接入方式
Nginx 中 `/api/` 转发到：

```nginx
proxy_pass http://127.0.0.1:9000/;
```

## 当前签名逻辑说明
当前实现包含：
- `Date` 头
- `Content-MD5`（有请求体时）
- `Authorization` 头
- 基于方法、内容摘要、类型、日期、路径的 HMAC-SHA256 签名

## 下一步建议
1. 用真实请求验证 `/api/v1/health`
2. 校验 FC Function Auth 是否完全兼容
3. 增加日志、重试、systemd 部署
