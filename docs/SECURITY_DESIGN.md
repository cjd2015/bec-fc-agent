# AI Agent Platform - 安全技术方案设计

**版本:** 1.0  
**更新日期:** 2026-03-30  
**域名:** datahive.site（已备案，证书已申请）

---

## 1️⃣ 安全威胁分析

### 1.1 OWASP Top 10 威胁

| 威胁 | 风险等级 | 说明 |
|------|----------|------|
| **XSS 攻击** | 🔴 高危 | 跨站脚本攻击 |
| **SQL 注入** | 🔴 高危 | SQL 注入攻击 |
| **CSRF 攻击** | 🔴 高危 | 跨站请求伪造 |
| **代码注入** | 🔴 高危 | 恶意代码执行 |
| **表单注入** | 🟠 中危 | 表单数据篡改 |
| **CSS 注入** | 🟠 中危 | CSS 选择器注入 |
| **CSS 伪造元素** | 🟠 中危 | 钓鱼攻击 |
| **明文存储** | 🔴 高危 | 敏感信息泄露 |
| **Token 校验** | 🔴 高危 | 身份认证绕过 |
| **会话劫持** | 🟠 中危 | 会话令牌盗用 |

---

## 2️⃣ 前端安全防护

### 2.1 XSS 防护

#### 威胁场景
- 攻击者注入恶意脚本
- 窃取用户 Cookie/Token
- 重定向到钓鱼网站
- 执行未授权操作

#### 防护措施

**1. React 自动转义**
```tsx
// ✅ 安全 - React 默认转义
<div>{userInput}</div>

// ❌ 危险 - 禁用转义
<div dangerouslySetInnerHTML={{ __html: userInput }} />
```

**2. 输入验证**
```typescript
// 白名单验证
const sanitizeInput = (input: string): string => {
  return input.replace(/[<>\"'&]/g, (char) => {
    const map: Record<string, string> = {
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
      '&': '&amp;',
    }
    return map[char] || char
  })
}
```

**3. Content Security Policy (CSP)**
```nginx
# Nginx 配置
add_header Content-Security-Policy "
  default-src 'self';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self';
  connect-src 'self' https://datahive.site;
  frame-ancestors 'none';
" always;
```

**4. HTTP Only Cookie**
```typescript
// 后端设置
res.cookie('token', token, {
  httpOnly: true,  // 禁止 JS 访问
  secure: true,    // 仅 HTTPS
  sameSite: 'strict',
  maxAge: 24 * 60 * 60 * 1000,
})
```

---

### 2.2 CSS 注入防护

#### 威胁场景
- 攻击者注入恶意 CSS
- 窃取用户输入（属性选择器攻击）
- 页面样式混乱
- 钓鱼 UI 覆盖

#### 防护措施

**1. 内联样式限制**
```tsx
// ✅ 安全 - 使用 className
<div className="user-content">{content}</div>

// ❌ 危险 - 动态 style
<div style={{ background: userColor }} />
```

**2. CSS 属性过滤**
```typescript
const sanitizeCSS = (css: string): string => {
  const dangerousPatterns = [
    /expression\s*\(/i,
    /javascript\s*:/i,
    /url\s*\(/i,
    /import\s+/i,
    /behavior\s*:/i,
  ]
  
  for (const pattern of dangerousPatterns) {
    if (pattern.test(css)) {
      throw new Error('Dangerous CSS detected')
    }
  }
  
  return css
}
```

**3. Shadow DOM 隔离**
```tsx
// 用户内容使用 Shadow DOM 隔离
const UserContent: React.FC<{ content: string }> = ({ content }) => {
  const ref = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    if (ref.current) {
      const shadow = ref.current.attachShadow({ mode: 'open' })
      shadow.innerHTML = `<style>/* 隔离样式 */</style><div>${content}</div>`
    }
  }, [content])
  
  return <div ref={ref} />
}
```

---

### 2.3 CSS 伪造元素防护

#### 威胁场景
- 攻击者创建覆盖层
- 伪造登录表单
- 诱导用户点击
- 窃取凭证

#### 防护措施

**1. 帧保护**
```nginx
# 禁止嵌入 iframe
add_header X-Frame-Options "DENY" always;
```

**2. UI 冗余检查**
```typescript
// 检测页面是否有覆盖层
const detectOverlay = (): boolean => {
  const overlays = document.querySelectorAll('[style*="position: fixed"]')
  return overlays.length > 1 // 允许多个固定元素
}
```

**3. 关键操作二次确认**
```tsx
// 删除、转账等关键操作
const confirmAction = async () => {
  const confirmed = await Modal.confirm({
    title: '确认删除',
    content: '此操作不可恢复，确定继续吗？',
    okText: '确定',
    cancelText: '取消',
  })
  return confirmed
}
```

---

### 2.4 表单注入防护

#### 威胁场景
- 篡改表单数据
- 绕过前端验证
- 提交恶意数据

#### 防护措施

**1. 服务端验证（必须）**
```typescript
// 后端验证（不能仅依赖前端）
const validateAgentCreate = (data: AgentCreateRequest) => {
  if (!data.name || data.name.length > 100) {
    throw new ValidationError('名称长度 1-100 字符')
  }
  
  if (data.temperature < 0 || data.temperature > 2) {
    throw new ValidationError('温度范围 0-2')
  }
  
  // ... 更多验证
}
```

**2. CSRF Token**
```tsx
// 前端添加 CSRF Token
const submitForm = async (data: FormData) => {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content
  
  await fetch('/api/v1/agent', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken,
    },
    body: JSON.stringify(data),
  })
}
```

**3. 请求来源验证**
```nginx
# Nginx 验证 Referer
if ($http_referer !~ "^https://(www\.)?datahive\.site") {
  return 403;
}
```

---

## 3️⃣ 后端安全防护

### 3.1 SQL 注入防护

#### 威胁场景
- 攻击者注入 SQL 代码
- 窃取数据库信息
- 篡改/删除数据

#### 防护措施

**1. 使用 ORM（已实现）**
```typescript
// ✅ 安全 - Sequelize 参数化查询
const agent = await Agent.findOne({ where: { id } })

// ❌ 危险 - 字符串拼接
const agent = await db.query(`SELECT * FROM agents WHERE id = ${id}`)
```

**2. 输入验证**
```typescript
// 验证 ID 格式
const validateId = (id: any): number => {
  const parsed = parseInt(id)
  if (isNaN(parsed) || parsed <= 0) {
    throw new ValidationError('无效的 ID')
  }
  return parsed
}
```

**3. 最小权限原则**
```sql
-- 数据库用户权限限制
CREATE USER 'agent_app'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON agent_db.* TO 'agent_app'@'localhost';
-- 不授予 DROP, CREATE, ALTER 权限
```

---

### 3.2 代码注入防护

#### 威胁场景
- 攻击者上传恶意代码
- 执行系统命令
- 控制服务器

#### 防护措施

**1. 文件上传限制**
```typescript
const uploadConfig = {
  allowedTypes: ['image/jpeg', 'image/png', 'image/gif'],
  allowedExtensions: ['.jpg', '.jpeg', '.png', '.gif'],
  maxSize: 5 * 1024 * 1024, // 5MB
  
  validate: (file: Express.Multer.File) => {
    if (!allowedTypes.includes(file.mimetype)) {
      throw new Error('不允许的文件类型')
    }
    
    if (file.size > maxSize) {
      throw new Error('文件过大')
    }
  },
}
```

**2. 禁用 eval**
```typescript
// ESLint 规则
'no-eval': 'error',
'no-implied-eval': 'error',
'no-new-function': 'error',
```

**3. 沙箱执行**
```typescript
// 使用 VM2 沙箱
const { VM } = require('vm2')

const executeUserCode = (code: string) => {
  const vm = new VM({
    timeout: 3000,
    sandbox: {},
  })
  
  try {
    return vm.run(code)
  } catch (e) {
    throw new Error('代码执行失败')
  }
}
```

---

### 3.3 敏感信息存储

#### 威胁场景
- 数据库泄露
- 密码明文存储
- API Key 泄露

#### 防护措施

**1. 密码加密（bcrypt + salt）**
```typescript
import bcrypt from 'bcrypt'

const SALT_ROUNDS = 12

// 加密密码
const hashPassword = async (password: string): Promise<string> => {
  const salt = await bcrypt.genSalt(SALT_ROUNDS)
  return bcrypt.hash(password, salt)
}

// 验证密码
const verifyPassword = async (password: string, hash: string): Promise<boolean> => {
  return bcrypt.compare(password, hash)
}
```

**2. API Key 加密存储**
```typescript
import crypto from 'crypto'

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY // 32 字节
const IV_LENGTH = 16

// 加密
const encrypt = (text: string): string => {
  const iv = crypto.randomBytes(IV_LENGTH)
  const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(ENCRYPTION_KEY), iv)
  let encrypted = cipher.update(text, 'utf8', 'hex')
  encrypted += cipher.final('hex')
  return iv.toString('hex') + ':' + encrypted
}

// 解密
const decrypt = (text: string): string => {
  const parts = text.split(':')
  const iv = Buffer.from(parts.shift()!, 'hex')
  const decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.from(ENCRYPTION_KEY), iv)
  let decrypted = decipher.update(parts.join(':'), 'hex', 'utf8')
  decrypted += decipher.final('utf8')
  return decrypted
}
```

**3. 环境变量管理**
```bash
# .env（不提交到 Git）
DATABASE_URL=postgresql://user:password@localhost:5432/agent
JWT_SECRET=your_super_secret_jwt_key_min_32_chars
ENCRYPTION_KEY=your_32_byte_encryption_key_here
API_KEYS_QWEN=sk-xxxxxxxx
```

```gitignore
# .gitignore
.env
.env.local
.env.production
*.key
*.pem
```

---

## 4️⃣ 身份认证与授权

### 4.1 Token 校验

#### JWT Token 实现

**1. Token 生成**
```typescript
import jwt from 'jsonwebtoken'

const JWT_SECRET = process.env.JWT_SECRET!
const JWT_EXPIRES_IN = '24h'

interface TokenPayload {
  userId: number
  username: string
  role: string
}

const generateToken = (payload: TokenPayload): string => {
  return jwt.sign(payload, JWT_SECRET, {
    expiresIn: JWT_EXPIRES_IN,
    issuer: 'datahive.site',
    audience: 'agent-platform',
  })
}
```

**2. Token 验证**
```typescript
const verifyToken = (token: string): TokenPayload => {
  try {
    return jwt.verify(token, JWT_SECRET, {
      issuer: 'datahive.site',
      audience: 'agent-platform',
    }) as TokenPayload
  } catch (e) {
    throw new UnauthorizedError('Token 无效或已过期')
  }
}
```

**3. 中间件验证**
```typescript
// Express 中间件
const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: '未提供认证令牌' })
  }
  
  const token = authHeader.substring(7)
  
  try {
    const payload = verifyToken(token)
    req.user = payload
    next()
  } catch (e) {
    return res.status(401).json({ error: '认证失败' })
  }
}
```

**4. Token 刷新机制**
```typescript
// 双 Token 机制（Access + Refresh）
const generateTokens = (payload: TokenPayload) => {
  const accessToken = generateToken({ ...payload, type: 'access' })
  const refreshToken = generateToken({ ...payload, type: 'refresh', exp: '7d' })
  
  return { accessToken, refreshToken }
}

// 刷新 Token
const refreshAccessToken = (refreshToken: string) => {
  const payload = verifyToken(refreshToken)
  
  if (payload.type !== 'refresh') {
    throw new Error('无效的刷新令牌')
  }
  
  return generateToken({ ...payload, type: 'access' })
}
```

---

### 4.2 会话安全

**1. 会话固定攻击防护**
```typescript
// 登录后重新生成会话 ID
const login = async (req: Request, res: Response) => {
  // 验证用户
  const user = await validateUser(req.body)
  
  // 销毁旧会话
  await req.session.destroy()
  
  // 创建新会话
  await req.session.regenerate()
  req.session.userId = user.id
  
  res.json({ success: true })
}
```

**2. 会话超时**
```typescript
// 会话配置
const sessionConfig = {
  secret: process.env.SESSION_SECRET!,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,        // HTTPS only
    httpOnly: true,      // 禁止 JS 访问
    sameSite: 'strict',  // CSRF 防护
    maxAge: 24 * 60 * 60 * 1000, // 24 小时
  },
}
```

---

## 5️⃣ HTTPS 与证书配置

### 5.1 SSL/TLS 配置

**域名:** datahive.site  
**证书状态:** ✅ 已配置完成  
**证书路径:** `/root/.openclaw/workspace/certs/datahive.site/`  
**配置文件:** `/root/.openclaw/workspace/projects/ai-agent-platform/config/nginx/ssl.conf`

#### Nginx 配置

```nginx
server {
    listen 80;
    server_name datahive.site www.datahive.site;
    
    # 强制 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name datahive.site www.datahive.site;
    
    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/datahive.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/datahive.site/privkey.pem;
    
    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    
    # 安全头
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://datahive.site; frame-ancestors 'none';" always;
    
    # 代理到后端
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### 5.2 证书自动续期

```bash
## 证书文件位置

```
/root/.openclaw/workspace/certs/datahive.site/
├── fullchain.pem     # 完整证书链（公钥）
├── privkey.pem       # 私钥（权限 600）
└── README.md         # 证书说明
```

## 部署步骤

```bash
# 1. 复制 Nginx 配置
sudo cp /root/.openclaw/workspace/projects/ai-agent-platform/config/nginx/ssl.conf \
  /etc/nginx/sites-available/datahive.site

# 2. 启用站点
sudo ln -s /etc/nginx/sites-available/datahive.site \
  /etc/nginx/sites-enabled/

# 3. 测试配置
sudo nginx -t

# 4. 重启 Nginx
sudo systemctl restart nginx

# 5. 验证 HTTPS
curl -I https://datahive.site
```

## 证书续期

**Let's Encrypt Certbot:**

```bash
# 安装
sudo apt install certbot python3-certbot-nginx

# 申请证书
sudo certbot --nginx -d datahive.site -d www.datahive.site

# 自动续期测试
sudo certbot renew --dry-run

# 设置自动续期（Cron）
sudo crontab -e
# 每天凌晨 2 点检查续期
0 2 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

**自动部署脚本:**

```bash
# 运行部署脚本
cd /root/.openclaw/workspace/projects/ai-agent-platform
./scripts/deploy-ssl.sh
```
```

---

## 6️⃣ 安全审计与监控

### 6.1 日志记录

```typescript
// 安全日志
const securityLogger = winston.createLogger({
  level: 'info',
  filename: 'logs/security.log',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
})

// 记录安全事件
const logSecurityEvent = (event: {
  type: string
  userId?: number
  ip: string
  userAgent: string
  details?: any
}) => {
  securityLogger.info('Security Event', event)
}

// 使用场景
logSecurityEvent({
  type: 'LOGIN_FAILED',
  ip: req.ip,
  userAgent: req.headers['user-agent'],
  details: { username: req.body.username },
})

logSecurityEvent({
  type: 'TOKEN_INVALID',
  ip: req.ip,
  userAgent: req.headers['user-agent'],
  details: { reason: 'expired' },
})
```

---

### 6.2 速率限制

```typescript
import rateLimit from 'express-rate-limit'

// 全局限流
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100, // 最多 100 次请求
  message: '请求过于频繁，请稍后再试',
  standardHeaders: true,
  legacyHeaders: false,
})

// 登录限流（更严格）
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5, // 15 分钟最多 5 次登录尝试
  message: '登录尝试次数过多，请 15 分钟后再试',
  skipSuccessfulRequests: true,
})

app.use('/api/v1/auth/login', loginLimiter)
```

---

### 6.3 入侵检测

```typescript
// 检测异常行为
const detectAnomalies = (req: Request) => {
  const ip = req.ip
  const userAgent = req.headers['user-agent']
  
  // 检查 IP 是否在黑名单
  if (isIPBlacklisted(ip)) {
    logSecurityEvent({ type: 'BLACKLISTED_IP', ip })
    return true
  }
  
  // 检查请求频率
  if (getRequestCount(ip) > 1000) {
    logSecurityEvent({ type: 'HIGH_FREQUENCY', ip, count: getRequestCount(ip) })
    return true
  }
  
  // 检查异常 User-Agent
  if (isSuspiciousUserAgent(userAgent)) {
    logSecurityEvent({ type: 'SUSPICIOUS_UA', ip, userAgent })
    return true
  }
  
  return false
}
```

---

## 7️⃣ 安全清单

### 7.1 开发阶段

- [ ] 所有输入都经过验证和转义
- [ ] 使用参数化查询（ORM）
- [ ] 密码使用 bcrypt 加密（salt rounds ≥ 12）
- [ ] 敏感信息使用 AES-256 加密存储
- [ ] 实现 JWT Token 认证
- [ ] 实现 CSRF Token 保护
- [ ] 配置 CORS 白名单
- [ ] 实现速率限制
- [ ] 记录安全日志
- [ ] 禁用 eval 和 Function 构造函数

### 7.2 部署阶段

- [ ] 配置 HTTPS（TLS 1.2+）
- [ ] 配置 HSTS
- [ ] 配置 CSP
- [ ] 配置 X-Frame-Options
- [ ] 配置 X-Content-Type-Options
- [ ] 配置 X-XSS-Protection
- [ ] 禁用目录列表
- [ ] 隐藏服务器版本信息
- [ ] 配置防火墙
- [ ] 定期更新依赖

### 7.3 运维阶段

- [ ] 定期安全审计
- [ ] 监控异常登录
- [ ] 监控异常请求
- [ ] 定期备份数据
- [ ] 定期更新证书
- [ ] 定期审查日志
- [ ] 定期渗透测试
- [ ] 制定应急响应计划

---

## 8️⃣ 应急响应

### 8.1 安全事件分级

| 级别 | 描述 | 响应时间 |
|------|------|----------|
| **P0** | 数据泄露、系统被控制 | 立即 |
| **P1** | 未授权访问、SQL 注入 | 1 小时内 |
| **P2** | XSS 攻击、暴力破解 | 4 小时内 |
| **P3** | 异常登录、可疑请求 | 24 小时内 |

### 8.2 应急响应流程

```
发现事件 → 初步评估 → 隔离系统 → 调查原因 → 修复漏洞 → 恢复服务 → 事后分析
```

---

## 9️⃣ 参考资料

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [Node.js 安全最佳实践](https://nodejs.org/en/docs/guides/security/)
- [React 安全指南](https://reactjs.org/docs/introducing-jsx.html#jsx-prevents-injection-attacks)
- [Express 安全最佳实践](https://expressjs.com/en/advanced/best-practice-security.html)

---

**文档版本:** 1.0  
**最后更新:** 2026-03-30  
**审核状态:** 待审核
