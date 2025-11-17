# 部署操作手册

完整的 Fitness Planner Agent 部署指南。

## 📋 目录

- [环境要求](#环境要求)
- [本地开发部署](#本地开发部署)
- [生产环境部署](#生产环境部署)
- [Docker 部署](#docker-部署)
- [数据库设置](#数据库设置)
- [环境变量配置](#环境变量配置)
- [HTTPS 配置](#https-配置)
- [监控和日志](#监控和日志)
- [备份策略](#备份策略)

---

## 环境要求

### 最低配置
- **CPU**: 2核
- **内存**: 4GB RAM
- **存储**: 20GB
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 10+

### 推荐配置
- **CPU**: 4核
- **内存**: 8GB RAM
- **存储**: 50GB SSD
- **操作系统**: Ubuntu 22.04 LTS

### 软件依赖
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.25+
- (可选) Nginx 1.18+
- (可选) Let's Encrypt / Certbot

---

## 本地开发部署

### 1. 克隆项目

\`\`\`bash
git clone https://github.com/yourusername/Fitness_Plan.git
cd Fitness_Plan
\`\`\`

### 2. 配置环境变量

\`\`\`bash
# 复制环境变量模板
cp backend/.env.example backend/.env

# 编辑环境文件
nano backend/.env
\`\`\`

**必填配置**:
\`\`\`bash
OPENAI_API_KEY=sk-your-api-key-here
DATABASE_URL=postgresql+asyncpg://fitness_user:fitness_password@localhost:5432/fitness_planner
SECRET_KEY=your-secret-key-generate-a-random-one
\`\`\`

### 3. 启动服务

\`\`\`bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 等待服务启动（约30秒）
\`\`\`

### 4. 验证部署

\`\`\`bash
# 检查服务状态
docker-compose ps

# 测试后端 API
curl http://localhost:8000/health

# 访问前端
open http://localhost:3000
\`\`\`

---

## 生产环境部署

### 准备工作

#### 1. 服务器设置

\`\`\`bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install -y curl git ufw fail2ban

# 配置防火墙
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
\`\`\`

#### 2. 安装 Docker

\`\`\`bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
\`\`\`

### 部署步骤

#### 1. 克隆项目

\`\`\`bash
cd /opt
sudo git clone https://github.com/yourusername/Fitness_Plan.git
sudo chown -R $USER:$USER Fitness_Plan
cd Fitness_Plan
\`\`\`

#### 2. 配置生产环境

\`\`\`bash
# 配置环境变量
cp backend/.env.example backend/.env
nano backend/.env
\`\`\`

**生产环境配置**:
\`\`\`bash
# 应用配置
DEBUG=False
ENVIRONMENT=production

# 数据库（使用强密码！）
DATABASE_URL=postgresql+asyncpg://fitness_user:STRONG_PASSWORD_HERE@db:5432/fitness_planner

# LLM 配置
OPENAI_API_KEY=sk-your-production-api-key

# 安全配置（生成强密钥！）
SECRET_KEY=use-python-secrets-token-urlsafe-to-generate

# CORS 配置（使用实际域名）
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
\`\`\`

#### 3. 生成安全密钥

\`\`\`bash
# 使用 Python 生成安全的 SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
\`\`\`

#### 4. 启动服务

\`\`\`bash
# 拉取镜像
docker-compose pull

# 启动服务（后台运行）
docker-compose up -d

# 查看日志确认启动成功
docker-compose logs -f backend
\`\`\`

#### 5. 初始化数据库

\`\`\`bash
# 运行数据库迁移（如果有）
docker-compose exec backend alembic upgrade head

# 创建管理员用户（如果需要）
docker-compose exec backend python -m app.cli create-admin
\`\`\`

---

## Docker 部署

### 使用 Docker Compose

**docker-compose.yml** 已配置好所有服务：

\`\`\`yaml
services:
  db:          # PostgreSQL 数据库
  backend:     # FastAPI 后端
  frontend:    # React 前端
\`\`\`

### 常用 Docker 命令

\`\`\`bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f [service_name]

# 进入容器
docker-compose exec backend bash
docker-compose exec db psql -U fitness_user -d fitness_planner

# 重建镜像
docker-compose build --no-cache

# 清理未使用的资源
docker system prune -a
\`\`\`

### 更新部署

\`\`\`bash
# 拉取最新代码
git pull origin main

# 重建并重启服务
docker-compose up -d --build

# 查看新容器状态
docker-compose ps
\`\`\`

---

## 数据库设置

### 手动创建数据库

\`\`\`bash
# 进入 PostgreSQL 容器
docker-compose exec db psql -U postgres

# 创建数据库和用户
CREATE DATABASE fitness_planner;
CREATE USER fitness_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fitness_planner TO fitness_user;
\q
\`\`\`

### 数据库备份

\`\`\`bash
# 备份数据库
docker-compose exec db pg_dump -U fitness_user fitness_planner > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker-compose exec -T db psql -U fitness_user fitness_planner < backup_20240117.sql
\`\`\`

### 数据库迁移

\`\`\`bash
# 使用 Alembic 管理迁移
docker-compose exec backend alembic upgrade head  # 升级到最新
docker-compose exec backend alembic downgrade -1  # 回退一个版本
\`\`\`

---

## HTTPS 配置

### 使用 Nginx 反向代理

#### 1. 安装 Nginx

\`\`\`bash
sudo apt install nginx -y
\`\`\`

#### 2. 配置 Nginx

\`\`\`bash
sudo nano /etc/nginx/sites-available/fitness-planner
\`\`\`

**配置内容**:
\`\`\`nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 前端
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 支持（如果需要）
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
\`\`\`

#### 3. 启用配置

\`\`\`bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/fitness-planner /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
\`\`\`

#### 4. 配置 SSL 证书

\`\`\`bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 测试自动续期
sudo certbot renew --dry-run
\`\`\`

---

## 监控和日志

### 日志管理

#### 查看日志

\`\`\`bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# 查看最近100行
docker-compose logs --tail=100 backend

# 查看实时日志（最近10行）
docker-compose logs -f --tail=10 backend
\`\`\`

#### 日志持久化

在 `docker-compose.yml` 中配置日志：

\`\`\`yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
\`\`\`

### 监控设置

#### 使用 Docker Stats

\`\`\`bash
# 查看容器资源使用情况
docker stats

# 查看特定容器
docker stats fitness_planner_backend
\`\`\`

#### 健康检查

\`\`\`bash
# 定期检查服务健康
curl http://localhost:8000/health

# 创建监控脚本
cat > monitor.sh << 'EOF'
#!/bin/bash
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Service is down! Restarting..."
    docker-compose restart backend
    # 发送告警通知
fi
EOF

chmod +x monitor.sh

# 添加到 crontab（每5分钟检查一次）
(crontab -l ; echo "*/5 * * * * /opt/Fitness_Plan/monitor.sh") | crontab -
\`\`\`

---

## 备份策略

### 自动备份脚本

\`\`\`bash
#!/bin/bash
# backup.sh - 自动备份脚本

BACKUP_DIR="/opt/backups/fitness_planner"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec -T db pg_dump -U fitness_user fitness_planner | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 备份环境配置
cp backend/.env $BACKUP_DIR/env_$DATE

# 保留最近30天的备份
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/db_$DATE.sql.gz"
\`\`\`

### 设置定时备份

\`\`\`bash
# 使脚本可执行
chmod +x backup.sh

# 添加到 crontab（每天凌晨2点备份）
(crontab -l ; echo "0 2 * * * /opt/Fitness_Plan/backup.sh") | crontab -
\`\`\`

---

## 安全最佳实践

### 1. 环境变量保护

\`\`\`bash
# 限制 .env 文件权限
chmod 600 backend/.env

# 不要提交 .env 到 git
echo ".env" >> .gitignore
\`\`\`

### 2. 数据库安全

- 使用强密码
- 限制数据库访问（仅内部网络）
- 定期备份

### 3. API 安全

- 启用 HTTPS
- 实施速率限制
- 使用 API 密钥认证

### 4. 系统安全

\`\`\`bash
# 配置 fail2ban 防止暴力攻击
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 禁用 root SSH 登录
sudo nano /etc/ssh/sshd_config
# 设置: PermitRootLogin no
sudo systemctl restart sshd
\`\`\`

---

## 故障恢复

### 服务无法启动

\`\`\`bash
# 检查日志
docker-compose logs backend

# 检查容器状态
docker-compose ps

# 完全重启
docker-compose down
docker-compose up -d
\`\`\`

### 数据库问题

\`\`\`bash
# 重启数据库
docker-compose restart db

# 检查数据库连接
docker-compose exec db psql -U fitness_user -d fitness_planner -c "SELECT 1"
\`\`\`

### 从备份恢复

\`\`\`bash
# 停止服务
docker-compose down

# 恢复数据库
docker-compose up -d db
gunzip < /opt/backups/fitness_planner/db_20240117.sql.gz | docker-compose exec -T db psql -U fitness_user fitness_planner

# 启动所有服务
docker-compose up -d
\`\`\`

---

## 性能优化

### Docker 优化

\`\`\`yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
\`\`\`

### 数据库优化

\`\`\`sql
-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_workout_sessions_user_id ON workout_sessions(user_id);
\`\`\`

---

## 常见问题

### Q: 如何更新到新版本？

\`\`\`bash
git pull origin main
docker-compose up -d --build
\`\`\`

### Q: 如何查看详细错误日志？

\`\`\`bash
docker-compose logs -f backend | grep ERROR
\`\`\`

### Q: 如何重置数据库？

\`\`\`bash
docker-compose down -v  # 删除所有卷
docker-compose up -d
\`\`\`

---

## 支持

- 📮 GitHub Issues
- 💬 Discussions
- 📧 Email: support@example.com

---

**最后更新**: 2024-11-17
