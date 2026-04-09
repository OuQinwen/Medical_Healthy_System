# GitHub 部署方案

本文档提供医学数据融合科研系统的GitHub部署方案，包括代码托管、CI/CD配置和自动化部署。

## 📋 目录

- [GitHub仓库设置](#github仓库设置)
- [项目结构优化](#项目结构优化)
- [CI/CD配置](#cicd配置)
- [部署方案](#部署方案)
- [环境配置](#环境配置)
- [监控和维护](#监控和维护)

## GitHub仓库设置

### 1. 创建GitHub仓库

```bash
# 在GitHub上创建新仓库
# 仓库名称: medical-data-fusion-system
# 可见性: Private (推荐) 或 Public
# 初始化: 不添加README、.gitignore或license
```

### 2. 本地仓库初始化

```bash
cd d:\文件\医学数据融合科研系统 - 副本
git init
git add .
git commit -m "Initial commit: 医学数据融合科研系统初始版本"
```

### 3. 连接远程仓库

```bash
git remote add origin https://github.com/your-username/medical-data-fusion-system.git
git branch -M main
git push -u origin main
```

### 4. 创建.gitignore文件

在项目根目录创建`.gitignore`文件：

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.egg-info/
dist/
build/

# Node.js
node_modules/
dist/
.nuxt/
.cache/
.vuepress/dist/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# 环境变量
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 数据文件
data/
uploads/
output/
temp_uploads/
*.xlsx
*.jpg
*.png
*.jpeg
*.pdf

# 数据库
*.db
*.sqlite
*.sqlite3

# 操作系统
.DS_Store
Thumbs.db

# 临时文件
*.tmp
*.temp
```

## 项目结构优化

### 推荐的GitHub仓库结构

```
medical-data-fusion-system/
├── .github/
│   ├── workflows/
│   │   ├── backend-ci.yml
│   │   ├── frontend-ci.yml
│   │   └── deploy.yml
│   └── ISSUE_TEMPLATE/
├── backend/              # 后端服务
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # 前端服务
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── agent/                # 数据处理Agent
│   ├── core/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── database/             # 数据库脚本
│   ├── migrations/
│   └── seeds/
├── docs/                 # 文档
├── docker-compose.yml
├── .gitignore
├── README.md
└── LICENSE
```

### 目录重命名脚本

```bash
# 重命名目录以符合标准结构
mv "后端服务器" backend
mv "可视化模块/医学数据融合科研系统" frontend
mv "数据agent" agent
mv "数据库" database
```

## CI/CD配置

### 1. 后端CI配置 (.github/workflows/backend-ci.yml)

```yaml
name: Backend CI

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'backend/**'
  pull_request:
    branches: [ main ]
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        cd backend
        pytest tests/ --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
```

### 2. 前端CI配置 (.github/workflows/frontend-ci.yml)

```yaml
name: Frontend CI

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'frontend/**'
  pull_request:
    branches: [ main ]
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run linter
      run: |
        cd frontend
        npm run lint
    
    - name: Run tests
      run: |
        cd frontend
        npm run test
    
    - name: Build
      run: |
        cd frontend
        npm run build
```

### 3. 部署配置 (.github/workflows/deploy.yml)

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /var/www/medical-data-fusion-system
          git pull origin main
          docker-compose down
          docker-compose pull
          docker-compose up -d --build
```

## 部署方案

### 方案一：Docker Compose部署（推荐）

#### 1. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: medical_mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: medical_research_system
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/migrations:/docker-entrypoint-initdb.d
    networks:
      - medical_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: medical_backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mysql:3306/medical_research_system
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - mysql
    volumes:
      - ./backend/uploads:/app/uploads
    networks:
      - medical_network

  agent:
    build:
      context: ./agent
      dockerfile: Dockerfile
    container_name: medical_agent
    ports:
      - "5000:5000"
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    networks:
      - medical_network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: medical_frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - medical_network

volumes:
  mysql_data:

networks:
  medical_network:
    driver: bridge
```

#### 2. 创建Dockerfile

**Backend Dockerfile (backend/Dockerfile)**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile (frontend/Dockerfile)**

```dockerfile
# 构建阶段
FROM node:16-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Agent Dockerfile (agent/Dockerfile)**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "main.py"]
```

#### 3. 部署步骤

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/medical-data-fusion-system.git
cd medical-data-fusion-system

# 2. 创建环境变量文件
cp .env.example .env
# 编辑.env文件，填入实际的配置

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 停止服务
docker-compose down
```

### 方案二：云平台部署

#### 1. AWS部署

**使用AWS Elastic Beanstalk**

```bash
# 安装EB CLI
pip install awsebcli

# 初始化EB应用
eb init -p docker medical-data-fusion-system

# 创建环境
eb create production-env

# 部署
eb deploy
```

#### 2. 阿里云部署

**使用阿里云容器服务ACK**

```bash
# 创建Kubernetes集群
# 配置kubectl连接到集群

# 部署应用
kubectl apply -f k8s/
```

## 环境配置

### GitHub Secrets配置

在GitHub仓库设置中添加以下Secrets：

```
SERVER_HOST=your-server.com
SERVER_USER=deploy
SSH_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----...
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_USER=medical_user
MYSQL_PASSWORD=your-password
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
```

### 服务器环境配置

创建`.env`文件：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://medical_user:password@localhost:3306/medical_research_system
MYSQL_ROOT_PASSWORD=root_password
MYSQL_USER=medical_user
MYSQL_PASSWORD=user_password

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Agent配置
OPENAI_API_KEY=your-openai-api-key
API_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4-vision-preview

# 服务配置
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
AGENT_HOST=0.0.0.0
AGENT_PORT=5000
```

## 监控和维护

### 1. 日志管理

```bash
# 查看容器日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f agent

# 日志轮转配置
# 在docker-compose.yml中添加：
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 2. 数据备份

```bash
# 数据库备份脚本
#!/bin/bash
BACKUP_DIR="/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
docker exec medical_mysql mysqldump -u root -p${MYSQL_ROOT_PASSWORD} medical_research_system > ${BACKUP_DIR}/backup_${DATE}.sql

# 保留最近7天的备份
find ${BACKUP_DIR} -name "backup_*.sql" -mtime +7 -delete
```

### 3. 健康检查

```yaml
# 在docker-compose.yml中添加健康检查
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### 4. 自动更新

```bash
# 创建更新脚本
#!/bin/bash
cd /var/www/medical-data-fusion-system
git pull origin main
docker-compose pull
docker-compose up -d --build
docker system prune -f
```

## 性能优化

### 1. 数据库优化

```sql
-- 添加索引
CREATE INDEX idx_patient_id ON lab_results(patient_id);
CREATE INDEX idx_exam_date ON imaging_reports(exam_date);
CREATE INDEX idx_upload_time ON file_uploads(upload_time);
```

### 2. 缓存配置

```python
# 使用Redis缓存
import redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

# 缓存患者数据
def get_patient_with_cache(patient_id: int):
    cache_key = f"patient_{patient_id}"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    # 从数据库获取
    data = get_patient_from_db(patient_id)
    redis_client.setex(cache_key, 3600, json.dumps(data))
    return data
```

## 安全加固

### 1. 防火墙配置

```bash
# 只开放必要端口
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### 2. SSL证书配置

```bash
# 使用Let's Encrypt
certbot --nginx -d your-domain.com
```

### 3. 定期更新

```bash
# 定期更新系统和依赖
apt update && apt upgrade -y
pip install --upgrade pip
npm update -g
```

## 故障排查

### 常见问题

1. **容器无法启动**
   ```bash
   # 查看详细日志
   docker-compose logs backend
   
   # 检查端口占用
   netstat -tulpn | grep :8000
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库状态
   docker-compose ps mysql
   
   # 测试连接
   docker exec -it medical_mysql mysql -u root -p
   ```

3. **前端无法访问后端**
   ```bash
   # 检查网络配置
   docker network inspect medical_network
   
   # 检查环境变量
   docker-compose config
   ```

## 回滚方案

```bash
# 回滚到上一个版本
git revert HEAD
docker-compose up -d --build

# 或回滚到指定提交
git checkout <commit-hash>
docker-compose up -d --build
```

---

**注意**: 部署前请确保：
1. 所有敏感信息已配置为环境变量
2. 数据库已正确初始化
3. 防火墙规则已正确配置
4. 备份策略已实施
5. 监控系统已配置