# 可视化模块

## 概述
可视化模块是医学数据融合科研系统的前端界面，基于Vue 3 + Vite构建，提供现代化的用户体验和响应式设计。

## 技术栈
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **语言**: TypeScript
- **路由**: Vue Router
- **样式**: Bootstrap CSS + Material Design
- **状态管理**: Pinia
- **UI组件**: 自定义组件

## 项目结构

```
src/
├── assets/          # 静态资源
├── components/      # 通用组件
├── router/          # 路由配置
├── stores/          # 状态管理
├── views/           # 页面视图
├── App.vue          # 根组件
└── main.ts          # 入口文件
```

## 核心页面

### 1. 登录页面 (NewLoginView)
- **文件**: `views/NewLoginView.vue`
- **功能**: 
  - 用户登录
  - 表单验证
  - 错误提示
  - 记住密码

### 2. 数据录入页面 (NewDataView)
- **文件**: `views/NewDataView.vue`
- **功能**:
  - 患者信息录入
  - 文件上传
  - OCR结果展示
  - 数据预览

### 3. 随访管理页面 (NewFollowUpView)
- **文件**: `views/NewFollowUpView.vue`
- **功能**:
  - 患者列表管理
  - 患者状态跟踪
  - 多分类文件上传
  - OCR结果展示
  - 数据导出

### 4. 质量控制页面 (NewQualityView)
- **文件**: `views/NewQualityView.vue`
- **功能**:
  - 数据质量检查
  - 异常数据标记
  - 质量报告生成

### 5. 科研分析页面 (NewResearchView)
- **文件**: `views/NewResearchView.vue`
- **功能**:
  - 数据统计分析
  - 图表可视化
  - 研究报告生成

### 6. 个人中心页面 (NewProFileView)
- **文件**: `views/NewProFileView.vue`
- **功能**:
  - 用户信息管理
  - 密码修改
  - API配置
  - 模型选择

## 核心组件

### 1. FileUpload (文件上传组件)
- **文件**: `components/Fileupload.vue`
- **功能**:
  - 单文件上传
  - 拖拽上传
  - 上传进度显示
  - 文件预览

### 2. MultiFileUpload (多文件上传组件)
- **文件**: `components/MultiFileUpload.vue`
- **功能**:
  - 多文件选择
  - 批量上传
  - 进度管理
  - 错误处理

### 3. AgentResultDisplay (OCR结果展示组件)
- **文件**: `components/AgentResultDisplay.vue`
- **功能**:
  - JSON数据展示
  - 格式化显示
  - 可折叠展开
  - 复制功能

### 4. LoadingOverLay (加载遮罩组件)
- **文件**: `components/LoadingOverLay.vue`
- **功能**:
  - 进度条显示
  - 步骤提示
  - 动画效果

### 5. MiniBarChart (迷你柱状图)
- **文件**: `components/MiniBarChart.vue`
- **功能**:
  - 数据可视化
  - 响应式设计
  - 颜色配置

### 6. MiniDonutChart (迷你环形图)
- **文件**: `components/MiniDonutChart.vue`
- **功能**:
  - 占比展示
  - 动画效果
  - 图例显示

### 7. MiniLineChart (迷你折线图)
- **文件**: `components/MiniLineChart.vue`
- **功能**:
  - 趋势展示
  - 多数据系列
  - 交互提示

## 状态管理

### auth (认证状态)
- **文件**: `stores/auth.ts`
- **功能**:
  - 用户登录状态
  - Token管理
  - 用户信息

### user (用户状态)
- **文件**: `stores/user.ts`
- **功能**:
  - 用户资料
  - 设置偏好
  - 模型配置

## 路由配置

### 路由列表
- `/` - 登录页面
- `/data` - 数据录入页面
- `/followup` - 随访管理页面
- `/quality` - 质量控制页面
- `/research` - 科研分析页面
- `/profile` - 个人中心页面

### 路由守卫
- **功能**: 
  - 验证用户登录状态
  - 重定向未登录用户
  - 保存路由状态

## API集成

### 基础配置
```typescript
const API_BASE_URL = 'http://localhost:8000'
```

### 主要API调用
- 用户认证
- 患者管理
- 文件上传
- 数据查询
- 配置管理

## 样式设计

### 设计原则
- Material Design风格
- 响应式布局
- 统一配色方案
- 现代化UI组件

### 主题颜色
- 主色: 蓝色系
- 成功: 绿色
- 警告: 黄色
- 错误: 红色
- 信息: 蓝色

### 响应式断点
- 移动端: < 768px
- 平板: 768px - 1024px
- 桌面: > 1024px

## 核心功能实现

### 1. 文件上传流程
1. 用户选择文件
2. 显示上传进度
3. 调用后端API
4. 处理OCR结果
5. 展示提取数据

### 2. 数据展示流程
1. 从后端获取数据
2. 格式化数据
3. 渲染组件
4. 用户交互
5. 数据更新

### 3. 状态管理流程
1. 初始化状态
2. 用户操作
3. 更新状态
4. 同步到后端
5. UI更新

## 用户体验优化

### 1. 加载优化
- 懒加载路由
- 组件按需加载
- 图片懒加载
- 代码分割

### 2. 交互优化
- 加载状态提示
- 错误提示
- 成功反馈
- 确认对话框

### 3. 性能优化
- 虚拟滚动
- 防抖节流
- 缓存策略
- 压缩资源

## 构建和部署

### 开发环境
```bash
npm install
npm run dev
```

### 生产构建
```bash
npm run build
```

### 预览构建
```bash
npm run preview
```

## 配置文件

### vite.config.ts
- 构建配置
- 插件配置
- 路径别名

### tsconfig.json
- TypeScript配置
- 编译选项
- 路径配置

## 浏览器兼容性

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 注意事项

1. **API地址**: 确保后端服务地址正确
2. **跨域处理**: 配置代理或CORS
3. **环境变量**: 使用.env文件管理配置
4. **依赖更新**: 定期更新依赖包
5. **代码规范**: 遵循ESLint和Prettier规则

## 维护建议

1. 定期更新依赖包
2. 优化构建配置
3. 监控性能指标
4. 收集用户反馈
5. 持续改进用户体验