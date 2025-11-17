# 故障排查指南

Fitness Planner Agent 常见问题和解决方案。

## 📋 目录

- [服务启动问题](#服务启动问题)
- [数据库连接问题](#数据库连接问题)
- [API 调用失败](#api-调用失败)
- [LLM 相关问题](#llm-相关问题)
- [前端问题](#前端问题)
- [性能问题](#性能问题)
- [Docker 相关问题](#docker-相关问题)

---

## 服务启动问题

### ❌ 问题: 容器启动失败

**症状**:
\`\`\`bash
docker-compose up -d
# 容器不断重启
\`\`\`

**排查步骤**:

1. **查看日志**:
\`\`\`bash
docker-compose logs backend
docker-compose logs db
\`\`\`

2. **检查端口占用**:
\`\`\`bash
# 检查 8000 端口
sudo lsof -i :8000
# 或
sudo netstat -tulpn | grep 8000

# 如果被占用，停止占用进程或更改端口
\`\`\`

3. **检查环境变量**:
\`\`\`bash
# 确保 .env 文件存在
ls -la backend/.env

# 检查必填配置
grep OPENAI_API_KEY backend/.env
grep DATABASE_URL backend/.env
\`\`\`

**常见原因**:
- 端口被占用
- 环境变量缺失或格式错误
- 数据库未就绪

**解决方案**:
\`\`\`bash
# 完全重启
docker-compose down
docker-compose up -d

# 如果还是失败，清理并重建
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
\`\`\`

---

### ❌ 问题: 后端 API 返回 503

**症状**:
\`\`\`bash
curl http://localhost:8000/health
# 返回 503 Service Unavailable
\`\`\`

**排查步骤**:

1. **检查容器状态**:
\`\`\`bash
docker-compose ps
# 确保 backend 容器状态为 Up
\`\`\`

2. **查看后端日志**:
\`\`\`bash
docker-compose logs -f backend
# 查找错误信息
\`\`\`

3. **检查数据库连接**:
\`\`\`bash
docker-compose exec backend python -c "
from app.core.database import engine
import asyncio
asyncio.run(engine.connect())
print('Database connection OK')
"
\`\`\`

**解决方案**:
- 等待服务完全启动（约30秒）
- 检查数据库是否正常运行
- 重启后端服务：`docker-compose restart backend`

---

## 数据库连接问题

### ❌ 问题: 数据库连接超时

**错误信息**:
\`\`\`
sqlalchemy.exc.OperationalError: could not connect to server
\`\`\`

**排查步骤**:

1. **检查数据库容器**:
\`\`\`bash
docker-compose ps db
# 确保状态为 healthy
\`\`\`

2. **测试数据库连接**:
\`\`\`bash
docker-compose exec db psql -U fitness_user -d fitness_planner -c "SELECT 1"
\`\`\`

3. **检查 DATABASE_URL**:
\`\`\`bash
# 确保 URL 格式正确
# postgresql+asyncpg://user:password@host:port/database
\`\`\`

**解决方案**:
\`\`\`bash
# 重启数据库
docker-compose restart db

# 如果还不行，重建数据库
docker-compose down
docker-compose up -d db
# 等待数据库就绪
sleep 10
docker-compose up -d backend
\`\`\`

---

### ❌ 问题: 数据库密码错误

**错误信息**:
\`\`\`
FATAL: password authentication failed for user "fitness_user"
\`\`\`

**解决方案**:

1. **重置数据库密码**:
\`\`\`bash
# 进入数据库容器
docker-compose exec db psql -U postgres

# 重置密码
ALTER USER fitness_user WITH PASSWORD 'new_password';
\q

# 更新 .env 文件中的密码
nano backend/.env
# 修改 DATABASE_URL

# 重启后端
docker-compose restart backend
\`\`\`

---

## API 调用失败

### ❌ 问题: CORS 错误

**症状**: 浏览器控制台显示
\`\`\`
Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:3000' 
has been blocked by CORS policy
\`\`\`

**解决方案**:

1. **检查 CORS 配置**:
\`\`\`bash
# backend/.env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
\`\`\`

2. **重启后端**:
\`\`\`bash
docker-compose restart backend
\`\`\`

3. **如果是生产环境**，添加实际域名：
\`\`\`bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
\`\`\`

---

### ❌ 问题: 422 Validation Error

**错误信息**:
\`\`\`json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
\`\`\`

**原因**: 请求体缺少必填字段或格式不正确

**解决方案**:

1. **检查 API 文档**:
\`\`\`bash
# 访问 Swagger UI
open http://localhost:8000/docs
\`\`\`

2. **验证请求格式**:
\`\`\`python
# 正确的请求格式
{
  "message": "我想制定训练计划",
  "include_history": true
}
\`\`\`

3. **检查数据类型**:
- 字符串需要用引号
- 数字不需要引号
- 布尔值：true/false（小写）

---

## LLM 相关问题

### ❌ 问题: OpenAI API 调用失败

**错误信息**:
\`\`\`
openai.error.AuthenticationError: Incorrect API key provided
\`\`\`

**解决方案**:

1. **验证 API Key**:
\`\`\`bash
# 测试 API Key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
\`\`\`

2. **更新环境变量**:
\`\`\`bash
nano backend/.env
# 确保 OPENAI_API_KEY 正确无误

# 重启后端
docker-compose restart backend
\`\`\`

---

### ❌ 问题: LLM 响应超时

**症状**: AI 响应时间过长或超时

**排查步骤**:

1. **检查网络连接**:
\`\`\`bash
# 测试到 OpenAI 的连接
curl -I https://api.openai.com
\`\`\`

2. **查看 LLM 配置**:
\`\`\`bash
# backend/.env
LLM_MODEL=gpt-4-turbo-preview
LLM_MAX_TOKENS=2000  # 减少可提高速度
\`\`\`

**优化方案**:
- 使用更快的模型（如 gpt-3.5-turbo）
- 减少 MAX_TOKENS
- 实施请求缓存

---

### ❌ 问题: LLM 响应格式错误

**症状**: Agent 返回的不是期望的 JSON 格式

**解决方案**:

1. **改进 Prompt**:
\`\`\`python
# 在 prompt 中明确要求 JSON 格式
prompt = """
请以以下 JSON 格式返回：
```json
{
  "field1": "value1",
  "field2": "value2"
}
```
"""
\`\`\`

2. **增加响应解析的容错性**:
\`\`\`python
try:
    data = json.loads(response)
except json.JSONDecodeError:
    # 尝试从 markdown 代码块中提取
    if "```json" in response:
        start = response.find("```json") + 7
        end = response.find("```", start)
        json_str = response[start:end].strip()
        data = json.loads(json_str)
\`\`\`

---

## 前端问题

### ❌ 问题: 前端白屏

**排查步骤**:

1. **检查浏览器控制台**:
- 按 F12 打开开发者工具
- 查看 Console 标签的错误信息

2. **检查网络请求**:
- 查看 Network 标签
- 确认 API 请求是否成功

3. **检查前端日志**:
\`\`\`bash
docker-compose logs frontend
\`\`\`

**常见原因**:
- API 地址配置错误
- CORS 问题
- JavaScript 语法错误

**解决方案**:
\`\`\`bash
# 重建前端
docker-compose up -d --build frontend

# 清除浏览器缓存
# Chrome: Ctrl+Shift+Delete
\`\`\`

---

### ❌ 问题: 前端无法连接后端

**症状**: 网络请求返回 ERR_CONNECTION_REFUSED

**解决方案**:

1. **检查后端是否运行**:
\`\`\`bash
curl http://localhost:8000/health
\`\`\`

2. **检查 Vite 代理配置**:
\`\`\`javascript
// frontend/vite.config.js
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://backend:8000',  // Docker 内部
        // 或 'http://localhost:8000'  // 本地开发
        changeOrigin: true,
      },
    },
  },
})
\`\`\`

---

## 性能问题

### ❌ 问题: API 响应慢

**排查步骤**:

1. **检查数据库查询**:
\`\`\`bash
# 启用 SQL 日志
# backend/.env
DATABASE_ECHO=True

# 查看慢查询
docker-compose logs backend | grep "SELECT"
\`\`\`

2. **检查 LLM 响应时间**:
\`\`\`bash
# 查看 Agent 调用日志
docker-compose logs backend | grep "LLM"
\`\`\`

3. **检查容器资源**:
\`\`\`bash
docker stats
\`\`\`

**优化方案**:
- 添加数据库索引
- 实施查询缓存
- 使用更快的 LLM 模型
- 增加容器资源限制

---

### ❌ 问题: 内存使用过高

**症状**: 容器被 OOM Killer 杀死

**解决方案**:

1. **限制容器内存**:
\`\`\`yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
\`\`\`

2. **优化 Python 内存使用**:
\`\`\`python
# 使用生成器而不是列表
# 及时关闭数据库连接
# 避免在内存中缓存大量数据
\`\`\`

---

## Docker 相关问题

### ❌ 问题: Docker 磁盘空间不足

**症状**:
\`\`\`
no space left on device
\`\`\`

**解决方案**:

1. **清理未使用的镜像和容器**:
\`\`\`bash
# 清理所有未使用的资源
docker system prune -a

# 清理卷
docker volume prune
\`\`\`

2. **检查磁盘使用**:
\`\`\`bash
docker system df
\`\`\`

---

### ❌ 问题: 容器无法访问网络

**排查步骤**:

1. **检查 Docker 网络**:
\`\`\`bash
docker network ls
docker network inspect fitness_plan_default
\`\`\`

2. **重建网络**:
\`\`\`bash
docker-compose down
docker network prune
docker-compose up -d
\`\`\`

---

## 日志分析技巧

### 查找特定错误

\`\`\`bash
# 查找错误日志
docker-compose logs backend | grep -i error

# 查找警告
docker-compose logs backend | grep -i warning

# 查找特定时间段的日志
docker-compose logs --since 2024-01-17T10:00:00 backend
docker-compose logs --until 2024-01-17T12:00:00 backend
\`\`\`

### 实时监控

\`\`\`bash
# 监控所有服务
watch -n 1 'docker-compose ps'

# 监控资源使用
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
\`\`\`

---

## 紧急恢复

### 完全重置系统

⚠️ **警告**: 这将删除所有数据！

\`\`\`bash
# 停止并删除所有容器和卷
docker-compose down -v

# 清理所有 Docker 资源
docker system prune -a --volumes

# 重新构建和启动
docker-compose build --no-cache
docker-compose up -d
\`\`\`

### 从备份恢复

\`\`\`bash
# 1. 停止服务
docker-compose down

# 2. 恢复数据库
docker-compose up -d db
sleep 10
gunzip < backup.sql.gz | docker-compose exec -T db psql -U fitness_user fitness_planner

# 3. 恢复环境配置
cp backup.env backend/.env

# 4. 启动所有服务
docker-compose up -d
\`\`\`

---

## 获取帮助

如果以上方法都无法解决问题：

1. **收集信息**:
\`\`\`bash
# 导出完整日志
docker-compose logs > logs.txt

# 导出系统信息
docker version > system_info.txt
docker-compose version >> system_info.txt
uname -a >> system_info.txt
\`\`\`

2. **提交 Issue**:
   - 访问: https://github.com/yourusername/Fitness_Plan/issues
   - 附上日志和系统信息
   - 描述问题的详细步骤

3. **社区支持**:
   - GitHub Discussions
   - 项目 Wiki
   - Email: support@example.com

---

## 常见问题 FAQ

**Q: 如何重置管理员密码？**
\`\`\`bash
docker-compose exec backend python -m app.cli reset-password --email admin@example.com
\`\`\`

**Q: 如何更改数据库密码？**
见上文"数据库密码错误"部分

**Q: 如何备份数据？**
见部署手册的"备份策略"部分

**Q: 如何查看 API 文档？**
访问 http://localhost:8000/docs

---

**最后更新**: 2024-11-17
