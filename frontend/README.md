# 旅行规划助手 - 前端项目

基于 Vue 3 + TypeScript + Vite 的现代化前端应用，提供智能旅行规划的用户界面。

## 技术栈

- **前端框架**: Vue 3 (组合式 API)
- **类型安全**: TypeScript
- **构建工具**: Vite
- **UI组件库**: Ant Design Vue
- **HTTP客户端**: Axios
- **路由管理**: Vue Router
- **地图组件**: 高德地图 (@amap/amap-jsapi-loader)

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

复制 `.env.example` 文件为 `.env`，并配置高德地图 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
VITE_AMAP_KEY=your-amap-api-key
VITE_API_BASE_URL=http://localhost:8000
```

**获取高德地图 API 密钥**:
1. 访问 [高德开放平台](https://console.amap.com/dev/key/app)
2. 注册/登录账号
3. 创建应用并获取 Web 服务 API Key

### 3. 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:3000 启动

### 4. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist` 目录

### 5. 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 接口定义
│   │   └── index.ts      # Axios 配置和 API 调用
│   ├── components/       # 组件
│   │   ├── AmapView.vue      # 高德地图组件
│   │   └── DayPlanDetail.vue # 单日行程详情组件
│   ├── router/           # 路由配置
│   │   └── index.ts
│   ├── types/            # TypeScript 类型定义
│   │   └── index.ts
│   ├── views/            # 页面组件
│   │   ├── Home.vue          # 首页（表单页）
│   │   └── PlanDetail.vue    # 行程详情页
│   ├── App.vue           # 根组件
│   └── main.ts           # 应用入口
├── index.html            # HTML 模板
├── package.json          # 项目依赖
├── tsconfig.json         # TypeScript 配置
├── vite.config.ts        # Vite 配置
└── env.d.ts              # 环境变量类型定义
```

## 功能特性

### 1. 旅行规划表单
- 目的地城市输入
- 日期范围选择
- 旅行天数设置
- 交通方式选择
- 住宿偏好选择
- 旅行偏好多选
- 额外要求输入

### 2. 行程详情展示
- 总体建议
- 预算明细（景点、住宿、餐饮、交通）
- 天气信息展示
- 每日行程详情
  - 景点信息（含地图定位）
  - 酒店信息（含地图定位）
  - 餐饮安排（含地图定位）
  - 天气信息

### 3. 地图集成
- 使用高德地图展示位置信息
- 支持标记点展示
- 支持信息窗口
- 自动调整视野范围

## API 接口

### POST /api/trip

创建旅行计划

**请求体**:
```typescript
{
  city: string              // 目的地城市
  start_date: string        // 开始日期 YYYY-MM-DD
  end_date: string          // 结束日期 YYYY-MM-DD
  travel_days: number       // 旅行天数 (1-30)
  transportation: string    // 交通方式
  accommodation: string     // 住宿偏好
  preferences: string[]     // 旅行偏好标签
  free_text_input?: string  // 额外要求
}
```

**响应**: TripPlan 对象

## 开发说明

### 代理配置

开发环境下，Vite 会将 `/api` 请求代理到后端服务（默认 http://localhost:8000）。配置在 `vite.config.ts` 中：

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

### 路由说明

- `/` - 首页（旅行规划表单）
- `/plan/:id?` - 行程详情页

### 数据存储

行程详情数据使用 `sessionStorage` 临时存储，页面刷新后会丢失。如需持久化，可改用其他存储方案。

## 注意事项

1. **API 超时设置**: 由于后端处理时间较长（约5-10分钟），Axios 超时时间设置为 10 分钟
2. **高德地图密钥**: 必须配置有效的高德地图 API 密钥才能正常显示地图
3. **后端服务**: 确保后端服务已启动并运行在 http://localhost:8000

## 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 许可证

MIT

