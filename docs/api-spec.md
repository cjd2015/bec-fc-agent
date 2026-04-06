# BEC 商务英语智能学习平台 - API 规范文档

**版本:** 1.0  
**更新时间:** 2026-03-31  
**适用范围:** MVP 核心 API

---

## 1. 文档目标

本文档用于统一 BEC 商务英语智能学习平台后端 API 的路径规范、请求方式、返回结构、鉴权规则和核心接口定义，指导前后端联调与后端实现。

---

## 2. 基础规范

### 2.1 API 前缀
所有接口统一使用：

```text
/api/v1
```

### 2.2 返回结构
成功响应示例：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

失败响应示例：

```json
{
  "code": 4001,
  "message": "invalid params",
  "data": null
}
```

### 2.3 鉴权方式
- 登录成功后返回 JWT Token
- 受保护接口通过 `Authorization: Bearer <token>` 传递

---

## 3. 健康检查接口

### 3.1 GET `/api/v1/health`
用于检查服务是否正常。

响应示例：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok"
  }
}
```

---

## 4. 用户与认证接口

### 4.1 POST `/api/v1/auth/register`
用户注册。

请求示例：
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "your_password"
}
```

响应示例：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "status": "active",
    "token": "jwt_token_here"
  }
}
```

### 4.2 POST `/api/v1/auth/login`
用户登录。

请求示例：
```json
{
  "username": "alice",
  "password": "your_password"
}
```

响应示例：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "alice",
    "status": "active",
    "token": "jwt_token_here"
  }
}
```

> ✅ 登录成功必须在后续请求头中添加 `Authorization: Bearer <token>`。

### 4.3 GET `/api/v1/users/profile`
获取当前用户画像。

### 4.4 PUT `/api/v1/users/profile`
更新当前用户画像。

请求示例：
```json
{
  "username": "alice",
  "display_name": "Alice Chen",
  "avatar_url": "https://...",
  "target_level": "BEC Intermediate",
  "current_level": "A2",
  "industry_background": "International Trade",
  "learning_goal": "Prepare for BEC and improve business speaking",
  "phone_number": "+86-10-12345678",
  "company": "DataHive",
  "job_title": "PM"
}
```

### 4.5 POST `/api/v1/users/password/change`
修改密码（需要提供旧密码）。

请求示例：
```json
{
  "username": "alice",
  "current_password": "oldP@ss",
  "new_password": "NewP@ssword1"
}
```

### 4.6 POST `/api/v1/users/password/forgot`
申请重置密码令牌（临时方案直接返回 token，后续可接入邮件/短信）。

请求示例：
```json
{
  "username": "alice"
}
```

响应示例：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "reset_token": "abcd...",
    "expires_at": "2026-04-02T00:00:00Z"
  }
}
```

### 4.7 POST `/api/v1/users/password/reset`
使用 token 重置密码。

请求示例：
```json
{
  "token": "abcd...",
  "new_password": "BrandNew123!"
}
```

---

## 5. 水平测试接口

### 5.1 GET `/api/v1/level-test/start`
获取测试题目。

### 5.2 POST `/api/v1/level-test/submit`
提交测试答案。

请求示例：
```json
{
  "answers": [
    {"question_id": 1, "user_answer": "A"},
    {"question_id": 2, "user_answer": "B"}
  ]
}
```

### 5.3 GET `/api/v1/level-test/result/{id}`
获取测试结果。

---

## 6. 单词学习接口

### 6.1 GET `/api/v1/vocab`
获取单词列表。

查询参数示例：
- `level`
- `tag`
- `page`
- `page_size`

### 6.2 GET `/api/v1/vocab/{id}`
获取单词详情。

### 6.3 POST `/api/v1/vocab/{id}/progress`
更新单词学习进度。

请求示例：
```json
{
  "learn_status": "review"
}
```

---

## 7. 句型学习接口

### 7.1 GET `/api/v1/patterns`
获取句型列表。

### 7.2 GET `/api/v1/patterns/{id}`
获取句型详情。

### 7.3 POST `/api/v1/patterns/{id}/progress`
更新句型学习进度。

请求示例：
```json
{
  "learn_status": "learned"
}
```

---

## 8. 场景训练接口

### 8.1 GET `/api/v1/scenes`
获取场景列表。

### 8.2 GET `/api/v1/scenes/{id}`
获取场景详情。

### 8.3 POST `/api/v1/scenes/{id}/start`
开始场景训练。

### 8.4 POST `/api/v1/scenes/{id}/message`
发送一轮对话消息。

请求示例：
```json
{
  "session_id": 1001,
  "message": "I would like to discuss the delivery schedule."
}
```

响应示例：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "reply": "Certainly, let's review the schedule.",
    "feedback": "Good opening sentence."
  }
}
```

### 8.5 POST `/api/v1/scenes/{id}/finish`
结束场景训练并生成总结。

---

## 9. 模拟考试接口

### 9.1 GET `/api/v1/mock-exams`
获取模考列表。

### 9.2 POST `/api/v1/mock-exams/{id}/submit`
提交模考答案。

### 9.3 GET `/api/v1/mock-exams/result/{id}`
获取模考结果。

---

## 10. 内容管理与审核接口

### 10.1 POST `/api/v1/content/import`
导入内容。

### 10.2 GET `/api/v1/content/review/pending`
获取待审核内容列表。

### 10.3 POST `/api/v1/content/review/{id}`
提交审核结果。

请求示例：
```json
{
  "review_result": "approved",
  "review_comment": "content is good"
}
```

### 10.4 POST `/api/v1/content/publish/{id}`
发布内容。

---

## 11. 错误码建议

| 错误码 | 含义 |
|---|---|
| 0 | 成功 |
| 4001 | 参数错误 |
| 4002 | 未登录或 Token 无效 |
| 4003 | 无权限 |
| 4041 | 资源不存在 |
| 5001 | 服务内部错误 |
| 5002 | 数据库错误 |
| 5003 | 外部模型调用失败 |

---

## 12. 安全要求

- 所有受保护接口必须鉴权
- 输入参数必须校验
- 不允许字符串拼接 SQL
- 不在响应中泄露敏感信息
- 审核/发布接口必须做权限控制

---

## 13. 结论

MVP 阶段 API 规范以“统一前缀、统一响应结构、统一鉴权方式”为核心，通过标准 RESTful 接口承载 BEC 商务英语平台的核心业务模块，为前后端联调与后端实现提供统一基线。
