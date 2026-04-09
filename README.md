# 医学数据融合科研系统

一个基于AI的医学数据融合与处理平台，支持多模态医学数据的自动化提取、验证、存储和分析。

## ✨ 特性

- 📤 多格式文件上传（图片、PDF等）
- 🔍 基于AI的OCR文字识别
- 📊 智能数据提取和结构化
- ✅ 自动数据验证和质量检查
- 👥 患者数据管理和随访
- 📈 检查结果和影像报告存储
- 🔐 用户认证和权限管理

## 🏗️ 技术栈

- **后端**: FastAPI (Python)
- **前端**: Vue.js 3 + Vite
- **数据库**: MySQL 8.0
- **AI服务**: 支持多种云端API

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 20+
- MySQL 8.0+

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/OuQinwen/Medical_Healthy_System
```

2. **配置数据库**
```bash
cd 数据库/BuildingTables
mysql -u root -p < create_all_tables.sql
```

3. **配置后端**
```bash
cd 后端服务器
pip install -r requirements.txt
cp .env.example .env
# 编辑.env文件，配置数据库连接
python main.py
```

4. **配置Agent**
```bash
cd 数据agent
pip install -r requirements.txt
cp .env.example .env
# 编辑.env文件，配置API密钥
python main.py
```

5. **配置前端**
```bash
cd 可视化模块/医学数据融合科研系统
npm install
npm run dev
```

## ⚙️ 配置

### 后端配置 (后端服务器/.env)

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/medical_research_system
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440
AGENT_BASE_URL=http://localhost:8001
```

### Agent配置 (数据agent/.env)

```env
API_KEY=your_api_key_here
API_BASE=your_api_base_url_here
VISION_MODEL=your_vision_model_here
LLM_MODEL=your_llm_model_here
```

## 📁 项目结构

```
医学数据融合科研系统/
├── 后端服务器/          # FastAPI后端
├── 可视化模块/          # Vue.js前端
├── 数据agent/           # 数据处理服务
├── 数据库/              # 数据库脚本
├── README.md            # 项目说明
├── DEPLOYMENT.md        # 部署指南
└── DEPENDENCIES.md      # 依赖说明
```

## 📖 文档

- [部署指南](DEPLOYMENT.md) - 详细的部署和配置说明
- [依赖说明](DEPENDENCIES.md) - 完整的依赖列表
- [数据库配置](数据库/SETUP.md) - 数据库安装和配置

## 🔐 安全

- 所有API接口需要认证
- 敏感信息使用环境变量
- 支持数据库连接池
- 文件上传限制

## 📄 许可证

MIT License

## ⚠️ 免责声明

本系统仅用于科研目的，不可用于临床诊断。使用前请确保遵守相关法律法规和医疗数据保护要求。
