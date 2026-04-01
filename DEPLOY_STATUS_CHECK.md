# 函数计算部署状态诊断

**时间:** 2026-03-30 18:11  
**状态:** ⚠️ 需要进一步确认

---

## 🔍 问题描述

用户在阿里云函数计算控制台没有看到函数列表。

---

## 📋 已尝试的部署

### 1. Serverless Devs 部署
```bash
cd fc-config
s deploy -y
```
**状态:** ⚠️ 日志不完整，无法确认

### 2. 阿里云 CLI 重新部署
```bash
./fix-deploy.sh
```
**状态:** ⚠️ 需要验证

---

## 🔧 诊断步骤

### 步骤 1：检查服务列表
```bash
aliyun fc ListServices
```

### 步骤 2：检查特定服务
```bash
aliyun fc GetService --serviceName ai-agent-service
```

### 步骤 3：检查函数列表
```bash
aliyun fc ListFunctions --serviceName ai-agent-service
```

### 步骤 4：检查触发器
```bash
aliyun fc GetTrigger \
  --serviceName ai-agent-service \
  --functionName agent-api \
  --triggerName http-trigger
```

---

## ⚠️ 可能的问题

### 问题 1：区域不匹配
**症状:** 部署在一个区域，在另一个区域查看

**解决:**
```bash
# 确认部署区域
export ALIYUN_REGION=cn-hangzhou

# 查看指定区域的服务
aliyun fc ListServices --region $ALIYUN_REGION
```

### 问题 2：AccountID 不匹配
**症状:** 使用了错误的 AccountID

**解决:**
```bash
# 获取当前 AccountID
aliyun sts GetCallerIdentity

# 确认与环境变量一致
echo $ALIYUN_USER_ID
```

### 问题 3：服务名称不一致
**症状:** s.yaml 中的服务名称与实际部署不一致

**检查:**
```bash
cat fc-config/s.yaml | grep "name:"
```

### 问题 4：权限问题
**症状:** 部署失败但无明确错误

**解决:**
```bash
# 检查 RAM 权限
aliyun ram ListPoliciesForUser --UserName <your-username>

# 需要的权限：
# - AliyunFCFullAccess
# - AliyunSTSAssumeRoleAccess
```

---

## 🛠️ 解决方案

### 方案 A：使用控制台查看

1. **访问函数计算控制台**
   ```
   https://fcnext.console.aliyun.com
   ```

2. **确认区域**
   - 选择：华东 1（杭州）

3. **查看服务列表**
   - 查找：ai-agent-service

4. **查看函数列表**
   - 点击服务 → 查看函数

---

### 方案 B：使用 CLI 验证

```bash
# 1. 获取 AccountID
aliyun sts GetCallerIdentity | grep AccountId

# 2. 列出所有服务
aliyun fc ListServices --region cn-hangzhou

# 3. 查看服务详情
aliyun fc GetService --serviceName ai-agent-service

# 4. 查看函数列表
aliyun fc ListFunctions --serviceName ai-agent-service
```

---

### 方案 C：重新部署

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform
./fix-deploy.sh
```

---

## 📊 验证清单

部署成功后应看到：

- [ ] 服务：ai-agent-service
- [ ] 函数：agent-api
- [ ] 触发器：http-trigger
- [ ] 访问地址：https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com

---

## 📝 需要的信息

请提供以下信息以便进一步诊断：

1. **控制台截图**
   - 函数计算服务列表
   - 选择的区域

2. **AccountID**
   ```bash
   aliyun sts GetCallerIdentity
   ```

3. **部署日志**
   ```bash
   cat /tmp/fc-redeploy.log
   ```

---

**下一步：** 请确认控制台中显示的区域和 AccountID
