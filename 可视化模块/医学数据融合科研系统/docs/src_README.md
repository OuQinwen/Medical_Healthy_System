# 医学智能数据融合科研系统

## 项目概述

医学智能数据融合科研系统是一个基于Vue 3 + TypeScript开发的现代化医学数据管理平台，专注于医疗数据的融合处理、随访管理、质量控制和科研分析。

## 技术栈

- **前端框架**: Vue 3 (Composition API)
- **开发语言**: TypeScript
- **构建工具**: Vite
- **路由管理**: Vue Router
- **状态管理**: Pinia
- **UI设计**: 原生CSS + 响应式布局

## 项目结构

```
src/
├── assets/          # 静态资源
│   ├── medical-icon.css      # 医疗图标样式
│   ├── data-input.css        # 数据输入组件样式
│   └── ...
├── components/      # 可复用组件
│   ├── MedicalIcon.vue       # 医疗红十字图标组件
│   ├── DataInput.vue         # 数据输入组件（支持文件上传）
│   ├── FileSelector.vue      # 文件选择器组件
│   ├── AddVisit.vue          # 创建随访表组件
│   └── VisitForm.vue         # 随访表展示组件
├── router/          # 路由配置
│   └── index.ts                # 路由定义
├── stores/          # 状态管理（Pinia）
├── views/           # 页面组件
│   ├── DataView.vue           # 数据处理页面
│   ├── VisitView.vue          # 随访管理页面
│   ├── DQMView.vue            # 数据质量管理页面
│   └── ScienceView.vue        # 科研分析页面
├── App.vue          # 应用根组件
└── main.ts          # 应用入口文件
```

## 核心功能模块

### 1. 数据处理 (/data)
- 文本消息输入和发送
- 支持多行文本输入
- 文件上传功能（图片、文本、表格）
- 文件类型验证和过滤
- 文件列表管理

### 2. 随访管理 (/visit)
- 创建患者随访表
- 患者基本信息管理
- 随访记录可视化展示
- 支持展开/收起详细信息
- 自动记录创建时间和创建人

### 3. 数据质量管理 (/dqm)
- 数据质量监控
- 数据清洗功能
- 质量报告生成

### 4. 科研分析 (/science)
- 科研数据分析
- 统计报告生成
- 数据可视化

## 设计特点

### 主题配色
- 主色调：医疗红色系 (#ef4444, #dc2626, #b91c1c)
- 背景色：浅红色渐变 (#fef2f2 → #fee2e2 → #fecaca)
- 强调色：白色和红色搭配

### 布局设计
- 响应式布局，中间50%区域展示内容
- 模块化设计，组件高度复用
- 卡片式布局，信息层次清晰
- 平滑动画过渡效果

### 用户体验
- 直观的导航界面
- 友好的交互反馈
- 完善的表单验证
- 优雅的错误提示

## 开发说明

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 类型检查
```bash
npm run type-check
```

## 组件说明

### 核心组件

#### MedicalIcon.vue
医疗红十字图标组件，用于品牌展示。

#### DataInput.vue
数据输入组件，支持文本和文件输入。
- 特性：自动高度调整、文件上传、文件类型过滤

#### FileSelector.vue
文件选择器组件，处理文件选择和管理。

#### AddVisit.vue
创建随访表单组件，包含患者基本信息表单。

#### VisitForm.vue
随访表展示组件，支持展开/收起详细信息。

## 数据模型

### VisitData 接口
```typescript
interface VisitData {
  patientName: string          // 患者姓名
  patientId: string            // 患者身份证号码
  gender: string               // 性别 (male/female)
  age: string                  // 年龄
  phone: string                // 联系电话
  preliminaryDiagnosis: string  // 初步诊断
  createTime: string           // 创建时间（ISO格式）
  creator: string              // 创建人
  notes: string                // 备注信息
}
```

## 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 开发规范

### 代码风格
- 使用 TypeScript 类型定义
- 使用 Composition API 编写组件
- 组件命名采用 PascalCase
- 文件命名采用 kebab-case

### Git 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建/工具相关

## 许可证

Copyright © 2026 医学智能数据融合科研系统