 # 项目依赖文档

本文档详细说明医学数据融合科研系统各个模块的依赖项和安装要求。

## 📋 目录

- [系统要求](#系统要求)
- [后端依赖](#后端依赖)
- [前端依赖](#前端依赖)
- [Agent依赖](#agent依赖)
- [数据库依赖](#数据库依赖)
- [安装说明](#安装说明)
- [常见问题](#常见问题)

## 系统要求

### 操作系统
- Windows 10/11
- Linux (Ubuntu 20.04+, CentOS 7+)
- macOS 10.15+

### 软件要求
- **Python**: 3.9 或更高版本
- **Node.js**: 20.19.0 或 22.12.0+
- **MySQL**: 8.0 或更高版本
- **Git**: 2.0 或更高版本
- **Docker** (可选): 20.10+
- **Docker Compose** (可选): 2.0+

## 后端依赖

### Python版本要求
- Python 3.9+

### 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| fastapi | 0.115.0 | 现代Web框架，构建高性能API |
| uvicorn[standard] | 0.32.0 | ASGI服务器，用于运行FastAPI应用 |
| python-multipart | 0.0.12 | 处理多部分表单数据（文件上传） |
| pydantic | 2.10.0 | 数据验证和设置管理 |
| requests | >=2.31.0 | HTTP请求库 |
| python-jose[cryptography] | 3.3.0 | JWT令牌处理 |
| passlib[bcrypt] | 1.7.4 | 密码哈希和验证 |
| python-dotenv | 1.0.0 | 环境变量管理 |
| bcrypt | 4.0.1 | 密码哈希算法 |

### 数据库依赖
- **PyMySQL**: MySQL数据库连接器
- **SQLAlchemy**: ORM框架
- **Alembic**: 数据库迁移工具（可选）

### 完整的requirements.txt

```txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-multipart==0.0.12
pydantic==2.10.0
requests>=2.31.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
bcrypt==4.0.1
pymysql>=1.0.0
sqlalchemy>=2.0.0
```

### 安装命令

```bash
cd 后端服务器
pip install -r requirements.txt
```

## 前端依赖

### Node.js版本要求
- Node.js 20.19.0 或 22.12.0+
- npm 9.0+ 或 yarn 1.22+

### 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| vue | 3.5.29 | 渐进式JavaScript框架 |
| vue-router | 5.0.3 | Vue.js官方路由管理器 |
| pinia | 3.0.4 | Vue.js状态管理库 |

### 开发依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| vite | 7.3.1 | 下一代前端构建工具 |
| typescript | 5.9.3 | JavaScript超集 |
| vue-tsc | 3.2.5 | Vue.js TypeScript编译器 |
| @vitejs/plugin-vue | 6.0.4 | Vite的Vue 3插件 |
| @vue/tsconfig | 0.8.1 | Vue TypeScript配置 |
| @tsconfig/node24 | 24.0.4 | Node.js TypeScript配置 |
| @types/node | 24.11.0 | Node.js类型定义 |
| vite-plugin-vue-devtools | 8.0.6 | Vue开发工具插件 |
| npm-run-all2 | 8.0.4 | 并行运行npm脚本 |

### 完整的package.json

```json
{
  "name": "medical-data-fusion-frontend",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "run-p type-check \"build-only {@}\" --",
    "preview": "vite preview",
    "build-only": "vite build",
    "type-check": "vue-tsc --build"
  },
  "dependencies": {
    "pinia": "^3.0.4",
    "vue": "^3.5.29",
    "vue-router": "^5.0.3"
  },
  "devDependencies": {
    "@tsconfig/node24": "^24.0.4",
    "@types/node": "^24.11.0",
    "@vitejs/plugin-vue": "^6.0.4",
    "@vue/tsconfig": "^0.8.1",
    "npm-run-all2": "^8.0.4",
    "typescript": "~5.9.3",
    "vite": "^7.3.1",
    "vite-plugin-vue-devtools": "^8.0.6",
    "vue-tsc": "^3.2.5"
  },
  "engines": {
    "node": "^20.19.0 || >=22.12.0"
  }
}
```

### 安装命令

```bash
cd 可视化模块/医学数据融合科研系统
npm install
```

或使用yarn：

```bash
cd 可视化模块/医学数据融合科研系统
yarn install
```

## Agent依赖

### Python版本要求
- Python 3.9+

### 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| requests | >=2.31.0 | HTTP请求库，调用API |
| python-dotenv | >=1.0.0 | 环境变量管理 |
| openpyxl | >=3.1.0 | Excel文件读写 |
| fastapi | >=0.115.0 | Web框架，提供API接口 |
| uvicorn[standard] | >=0.32.0 | ASGI服务器 |
| python-multipart | >=0.0.12 | 文件上传支持 |
| pydantic | >=2.10.0 | 数据验证 |

### AI/ML依赖（可选）

| 包名 | 版本 | 用途 |
|------|------|------|
| openai | >=1.0.0 | OpenAI API客户端 |
| Pillow | >=10.0.0 | 图像处理 |
| pytesseract | >=0.3.0 | OCR引擎 |

### 完整的requirements.txt

```txt
# 医学OCR Agent 依赖包

# HTTP请求库
requests>=2.31.0

# 环境变量管理
python-dotenv>=1.0.0

# Excel文件处理
openpyxl>=3.1.0

# FastAPI Web框架
fastapi>=0.115.0

# ASGI服务器
uvicorn[standard]>=0.32.0

# 文件上传支持
python-multipart>=0.0.12

# Pydantic数据验证
pydantic>=2.10.0

# AI/ML依赖（可选）
openai>=1.0.0
Pillow>=10.0.0
pytesseract>=0.3.0
```

### 安装命令

```bash
cd 数据agent
pip install -r requirements.txt
```

## 数据库依赖

### MySQL版本要求
- MySQL 8.0+ 或 MariaDB 10.5+

### 推荐配置

```ini
[mysqld]
# 字符集设置
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

# 连接设置
max_connections=200
max_connect_errors=100

# 缓冲区设置
innodb_buffer_pool_size=1G
key_buffer_size=256M

# 日志设置
log_error=mysql_error.log
slow_query_log=1
long_query_time=2
```

### Python MySQL客户端

```txt
pymysql>=1.0.0
cryptography>=41.0.0
```

## 安装说明

### 1. 系统级依赖安装

#### Windows
```powershell
# 安装Python
# 从 https://www.python.org/downloads/ 下载安装

# 安装Node.js
# 从 https://nodejs.org/ 下载安装

# 安装MySQL
# 从 https://dev.mysql.com/downloads/mysql/ 下载安装

# 安装Git
# 从 https://git-scm.com/downloads 下载安装
```

#### Linux (Ubuntu/Debian)
```bash
# 更新包列表
sudo apt update

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv

# 安装Node.js和npm
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 安装MySQL
sudo apt install mysql-server

# 安装Git
sudo apt install git
```

#### macOS
```bash
# 使用Homebrew安装
brew install python@3.9
brew install node
brew install mysql
brew install git
```

### 2. Python虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
```

### 3. 后端依赖安装

```bash
cd 后端服务器
pip install -r requirements.txt
```

### 4. Agent依赖安装

```bash
cd 数据agent
pip install -r requirements.txt
```

### 5. 前端依赖安装

```bash
cd 可视化模块/医学数据融合科研系统
npm install
```

### 6. 数据库初始化

```bash
cd 数据库/BuildingTables
mysql -u root -p < create_all_tables.sql
```

## 版本兼容性

### Python版本兼容性

| Python版本 | 后端 | Agent | 状态 |
|------------|------|-------|------|
| 3.9 | ✅ | ✅ | 完全支持 |
| 3.10 | ✅ | ✅ | 完全支持 |
| 3.11 | ✅ | ✅ | 完全支持 |
| 3.12 | ✅ | ✅ | 完全支持 |
| 3.13 | ⚠️ | ⚠️ | 测试中 |

### Node.js版本兼容性

| Node.js版本 | 前端 | 状态 |
|-------------|------|------|
| 18.x | ⚠️ | 部分支持 |
| 20.19.0+ | ✅ | 完全支持 |
| 22.12.0+ | ✅ | 完全支持 |

### MySQL版本兼容性

| MySQL版本 | 状态 |
|-----------|------|
| 5.7 | ❌ | 不支持 |
| 8.0 | ✅ | 完全支持 |
| 8.4+ | ✅ | 完全支持 |

## 常见问题

### 1. Python依赖安装失败

**问题**: pip安装依赖时出现错误

**解决方案**:
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或者使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 2. Node.js依赖安装失败

**问题**: npm install失败或很慢

**解决方案**:
```bash
# 清除npm缓存
npm cache clean --force

# 使用国内镜像
npm config set registry https://registry.npmmirror.com

# 重新安装
rm -rf node_modules package-lock.json
npm install
```

### 3. MySQL连接失败

**问题**: 无法连接到MySQL数据库

**解决方案**:
```bash
# 检查MySQL服务状态
# Windows:
net start mysql

# Linux:
sudo systemctl status mysql
sudo systemctl start mysql

# 检查端口占用
netstat -an | grep 3306

# 测试连接
mysql -u root -p -h localhost
```

### 4. 虚拟环境问题

**问题**: 激活虚拟环境失败

**解决方案**:
```bash
# Windows PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1

# 重新创建虚拟环境
python -m venv --clear venv
```

### 5. 权限问题

**问题**: 安装依赖时权限不足

**解决方案**:
```bash
# Linux/macOS - 使用用户安装
pip install --user -r requirements.txt

# 或使用虚拟环境（推荐）
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 依赖更新

### 定期更新依赖

```bash
# 更新Python依赖
pip list --outdated
pip install --upgrade package-name

# 更新Node.js依赖
npm outdated
npm update package-name
```

### 依赖安全检查

```bash
# Python依赖安全检查
pip install safety
safety check

# Node.js依赖安全检查
npm audit
npm audit fix
```

## 开发环境设置

### VSCode推荐扩展

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "Vue.volar",
    "Vue.vscode-typescript-vue-plugin",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode"
  ]
}
```

### 环境变量模板

创建`.env.example`文件：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/medical_research_system
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_USER=medical_user
MYSQL_PASSWORD=your_password

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API配置
OPENAI_API_KEY=your-openai-api-key
API_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4-vision-preview

# 服务配置
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
AGENT_HOST=0.0.0.0
AGENT_PORT=5000
```

## 性能优化建议

### 1. 使用生产级依赖

```bash
# 使用uv代替pip（更快）
pip install uv

# 安装依赖
uv pip install -r requirements.txt
```

### 2. 缓存依赖

```bash
# Docker构建缓存
# 在Dockerfile中优先复制依赖文件
COPY requirements.txt .
RUN pip install -r requirements.txt

# 前端依赖缓存
COPY package*.json ./
RUN npm ci
```

### 3. 依赖精简

```bash
# 分析未使用的依赖
pip install pipdeptree
pipdeptree --reverse

# 移除未使用的依赖
pip-autoremove
```

---

**最后更新**: 2026-04-08
**维护者**: 医学数据融合科研系统团队