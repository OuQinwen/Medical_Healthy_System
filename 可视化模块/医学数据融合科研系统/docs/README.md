# 医学数据融合科研系统 - 前端可视化

## 概述

前端基于Vue 3 + TypeScript + Vite构建，提供现代化的医学数据管理和分析界面。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript
- **构建工具**: Vite
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **UI样式**: 自定义CSS（类似Material Design）
- **HTTP客户端**: Fetch API

## 项目结构

```
可视化模块/医学数据融合科研系统/
├── index.html             # HTML入口文件
├── package.json           # 项目依赖配置
├── vite.config.ts         # Vite配置
├── tsconfig.json          # TypeScript配置
├── .gitignore            # Git忽略文件
├── src/                   # 源代码目录
│   ├── main.ts           # 应用入口
│   ├── App.vue           # 根组件
│   ├── Newstyle.css      # 全局样式
│   ├── router/           # 路由配置
│   │   └── index.ts
│   ├── stores/           # 状态管理
│   │   ├── auth.ts       # 认证状态
│   │   └── user.ts       # 用户状态
│   ├── views/            # 页面组件
│   │   ├── NewLoginView.vue      # 登录页
│   │   ├── NewDataView.vue       # 数据处理页
│   │   ├── NewFollowUpView.vue   # 随访管理页
│   │   ├── NewQualityView.vue    # 数据质量管理页
│   │   ├── NewResearchView.vue   # 科研分析页
│   │   └── NewProFileView.vue    # 个人中心页
│   ├── components/       # 公共组件
│   │   ├── AgentResultDisplay.vue  # Agent结果显示
│   │   ├── ButtomNav.vue          # 底部导航
│   │   ├── DataInput.vue          # 数据输入
│   │   ├── FileSelector.vue       # 文件选择器
│   │   ├── Fileupload.vue         # 文件上传
│   │   ├── LoadingOverLay.vue     # 加载遮罩
│   │   ├── MiniBarChart.vue       # 迷你柱状图
│   │   ├── MiniDonutChart.vue     # 迷你环形图
│   │   ├── MiniLineChart.vue      # 迷你折线图
│   │   └── NewOCRResult.vue       # OCR结果显示
│   └── assets/           # 静态资源
│       ├── main.css
│       ├── base.css
│       ├── data-input.css
│       └── hero.png
├── public/               # 公共资源目录
├── docs/                 # 文档目录
│   ├── README.md        # 本文档
│   ├── 后端开发备忘录.md
│   └── src_README.md
├── dist/                # 构建输出目录
└── test/                # 测试目录
```

## 核心功能模块

### 1. 路由管理 (router/index.ts)

#### 路由列表
- `/` - 重定向到 /data
- `/login` - 登录页面
- `/data` - 数据处理页面
- `/visit` - 随访管理页面
- `/dqm` - 数据质量管理页面
- `/science` - 科研分析页面
- `/mine` - 个人中心页面

#### 路由守卫
- 检查用户认证状态
- 未认证用户重定向到登录页
- 已认证用户访问登录页重定向到主页

### 2. 状态管理 (stores/)

#### auth.ts - 认证状态
- 管理用户登录状态
- 存储和读取token
- 用户信息管理

#### user.ts - 用户状态
- 用户信息管理
- 用户偏好设置

### 3. 页面组件

#### NewLoginView.vue - 登录页
**功能**
- 用户登录
- 表单验证
- 错误提示
- 记住密码

#### NewDataView.vue - 数据处理页
**功能**
- 数据展示
- 数据筛选
- 数据统计

#### NewFollowUpView.vue - 随访管理页
**功能**
- 患者列表管理
- 患者信息展示
- 文件上传和管理
- OCR结果显示
- 数据统计
- 患者筛选和搜索

**核心功能**
- 新增患者
- 患者详情查看
- 上传资料文件（人口学信息/过往手术史/检查结果/其他）
- OCR提取结果显示
- 数据验证结果展示

#### NewQualityView.vue - 数据质量管理页
**功能**
- 数据质量监控
- 数据验证
- 错误提示

#### NewResearchView.vue - 科研分析页
**功能**
- 数据分析
- 图表展示
- 统计报告

#### NewProFileView.vue - 个人中心页
**功能**
- 个人信息管理
- 密码修改
- 系统设置

### 4. 公共组件

#### AgentResultDisplay.vue - Agent结果显示
**功能**
- 显示OCR提取结果
- 显示数据验证结果
- 错误信息提示

#### FileSelector.vue - 文件选择器
**功能**
- 文件选择
- 文件预览
- 文件删除

#### Fileupload.vue - 文件上传
**功能**
- 文件上传
- 上传进度显示
- 上传结果提示

#### MiniBarChart.vue - 迷你柱状图
**功能**
- 数据可视化
- 小型统计图表

#### MiniDonutChart.vue - 迷你环形图
**功能**
- 数据占比显示
- 小型统计图表

#### MiniLineChart.vue - 迷你折线图
**功能**
- 趋势数据展示
- 小型统计图表

## API接口调用

### 认证接口

#### 登录
```typescript
const login = async (username: string, password: string) => {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  })
  const result = await response.json()
  if (result.access_token) {
    localStorage.setItem('token', result.access_token)
  }
  return result
}
```

#### 获取当前用户
```typescript
const getCurrentUser = async () => {
  const token = localStorage.getItem('token')
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  return await response.json()
}
```

### 患者管理接口

#### 获取患者列表
```typescript
const getPatients = async () => {
  const token = localStorage.getItem('token')
  const response = await fetch(`${API_BASE_URL}/api/patients`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  return await response.json()
}
```

#### 创建患者
```typescript
const createPatient = async (patientData: any) => {
  const token = localStorage.getItem('token')
  const response = await fetch(`${API_BASE_URL}/api/patients`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(patientData)
  })
  return await response.json()
}
```

### 文件上传接口

#### 上传患者文件
```typescript
const uploadPatientFile = async (patientName: string, category: string, files: File[]) => {
  const token = localStorage.getItem('token')
  const formData = new FormData()
  files.forEach(file => {
    formData.append('files', file)
  })
  formData.append('component_name', category)
  formData.append('enable_ocr', 'true')
  formData.append('model_type', 'cloud')

  const response = await fetch(`${API_BASE_URL}/api/patient/${encodeURIComponent(patientName)}/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  })
  return await response.json()
}
```

## 样式系统

### 设计原则
- 现代化、简洁、专业
- 医疗科技风格
- 响应式设计
- 无障碍支持

### 颜色主题
```css
--primary-color: #2563eb;
--secondary-color: #64748b;
--success-color: #10b981;
--warning-color: #f59e0b;
--error-color: #ef4444;
--background-color: #f8fafc;
--surface-color: #ffffff;
--text-primary: #1e293b;
--text-secondary: #64748b;
```

### 组件样式
- 按钮样式
- 输入框样式
- 卡片样式
- 表格样式
- 模态框样式

## 安装和运行

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
```

### 生产构建
```bash
npm run build
```

### 预览生产构建
```bash
npm run preview
```

### 类型检查
```bash
npm run type-check
```

## 配置说明

### Vite配置 (vite.config.ts)
```typescript
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### TypeScript配置 (tsconfig.json)
- 严格模式开启
- 路径别名配置
- Vue组件类型支持

## 开发指南

### 创建新页面
1. 在 `src/views/` 目录创建Vue组件
2. 在 `src/router/index.ts` 添加路由
3. 在底部导航中添加入口（如需要）

### 创建新组件
1. 在 `src/components/` 目录创建Vue组件
2. 在需要的页面中引入使用
3. 添加组件类型定义

### 状态管理
1. 在 `src/stores/` 目录创建store
2. 使用Pinia进行状态管理
3. 在组件中引入和使用

## 测试

### 测试目录
测试脚本位于 `test/` 目录

### 测试功能
- 组件测试
- 页面测试
- API测试

## 性能优化

### 优化建议
1. **代码分割**: 使用动态导入
2. **懒加载**: 路由懒加载
3. **图片优化**: 压缩图片资源
4. **缓存策略**: 合理使用缓存
5. **打包优化**: 减少包体积

### 构建优化
- 启用Tree Shaking
- 代码压缩
- 资源压缩

## 部署

### 部署步骤
1. 构建生产版本: `npm run build`
2. 将 `dist/` 目录内容部署到服务器
3. 配置Nginx或Apache服务器
4. 配置HTTPS

### Nginx配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 浏览器兼容性

### 支持的浏览器
- Chrome (最新版本)
- Firefox (最新版本)
- Safari (最新版本)
- Edge (最新版本)

### Polyfill
根据需要添加必要的polyfill

## 扩展建议

### 功能扩展
- [ ] 添加国际化支持
- [ ] 添加主题切换
- [ ] 添加离线功能
- [ ] 添加数据导出功能
- [ ] 添加打印功能

### 技术优化
- [ ] 添加单元测试
- [ ] 添加E2E测试
- [ ] 优化首屏加载
- [ ] 添加错误监控
- [ ] 添加性能监控

## 安全注意事项

1. **XSS防护**: 对用户输入进行转义
2. **CSRF防护**: 使用CSRF token
3. **敏感信息**: 不要在localStorage存储敏感信息
4. **HTTPS**: 生产环境使用HTTPS
5. **CSP**: 配置内容安全策略

## 维护说明

### 日志管理
- 前端错误日志
- API调用日志
- 用户行为日志

### 版本更新
- 定期更新依赖包
- 测试新版本兼容性
- 查看安全更新

### 文档维护
- 保持代码注释更新
- 更新README文档
- 记录重要变更

## 联系方式

如有问题或建议，请联系开发团队。

---

**最后更新**: 2026-03-27
**版本**: 1.0.0