# 旅行规划助手 (Trip Planner)

一个基于AI的智能旅行规划全栈系统，能够根据用户需求自动生成详细的旅行计划，包括景点推荐、天气信息、住宿安排、餐饮建议和预算估算。

## 🌟 功能特点

- **智能景点推荐**：基于用户偏好和目的地自动推荐合适的景点
- **天气信息查询**：获取旅行期间的详细天气预报
- **住宿安排建议**：推荐符合用户偏好的酒店住宿
- **餐饮计划推荐**：提供每日三餐的推荐和预算
- **个性化行程规划**：根据时间和景点位置优化行程安排
- **预算估算**：提供详细的费用预算，包括景点门票、住宿、餐饮和交通
- **精美旅行手册**：自动生成HTML格式的可视化旅行手册和PNG图片
- **交互式地图**：使用高德地图展示景点、酒店、餐厅位置
- **现代化前端界面**：基于Vue 3的响应式用户界面

## 🛠 技术架构

### 后端技术栈

- **Web框架**: FastAPI
- **AI框架**: LangChain
- **多智能体系统**: 基于LangChain的多智能体架构
- **地图服务**: 高德地图MCP工具
- **LLM支持**: DeepSeek/OpenAI等兼容OpenAI API的模型

### 前端技术栈

- **前端框架**: Vue 3 (组合式 API)
- **类型安全**: TypeScript
- **构建工具**: Vite
- **UI组件库**: Ant Design Vue
- **HTTP客户端**: Axios
- **路由管理**: Vue Router
- **地图组件**: 高德地图 (@amap/amap-jsapi-loader)

### 多智能体系统

本项目采用多智能体架构，利用多个专门的AI代理协同工作：

- **景点搜索专家**：负责搜索和筛选目标城市的景点
- **天气查询专家**：获取旅行期间的天气信息
- **酒店推荐专家**：推荐合适的住宿选择
- **美食推荐专家**：提供餐饮建议
- **行程规划专家**：整合所有信息生成最优旅行计划
- **手册制作专家**：将旅行计划转化为精美的HTML手册

## 🚀 快速开始

### 环境要求

- Python 3.12
- Node.js 18+ 和 npm
- 高德地图API密钥（获取指南：https://amap.apifox.cn/doc-537183）
- LLM API密钥 (DeepSeek/OpenAI)

### 安装步骤

#### 1. 克隆项目仓库

```bash
git clone https://github.com/YAYUN123/trip_planner.git
cd trip_planner
```

#### 2. 后端配置

```bash
cd backend

# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量
cp .env_example .env
```

在 `backend/.env` 文件中配置以下API密钥：

```
GAODE_API_KEY="your_amap_api_key"
LLM_API_KEY="your_llm_api_key"
LLM_MODEL_ID="your_preferred_model"
LLM_BASE_URL="your_llm_base_url"
```

#### 3. 前端配置

```bash
cd ../frontend

# 安装Node.js依赖
npm install

# 配置环境变量
cp .env.example .env
```

在 `frontend/.env` 文件中配置：

```
VITE_AMAP_KEY=your-amap-api-key
VITE_API_BASE_URL=http://localhost:8000
```

**获取高德地图 API 密钥**:
1. 访问 [高德开放平台](https://console.amap.com/dev/key/app)
2. 注册/登录账号
3. 创建应用并获取 Web 服务 API Key

#### 4. 启动服务

**启动后端服务**（在 `backend` 目录下）：

```bash
uvicorn main:app --reload
```

后端服务将在 http://localhost:8000 启动

**启动前端服务**（在 `frontend` 目录下，新开一个终端）：

```bash
npm run dev
```

前端应用将在 http://localhost:3000 启动

## 📁 项目结构

```
trip_planner/
├── backend/                 # 后端服务
│   ├── main.py             # FastAPI主程序入口，包含多智能体系统
│   ├── data_model.py       # 数据模型定义
│   ├── parse_info.py       # 数据解析工具
│   ├── prompts.py          # AI提示词模板
│   ├── cluster.py          # 景点聚类算法
│   ├── troubleshooting.py  # 故障排查工具
│   ├── requirements.txt    # Python依赖
│   └── README.md           # 后端文档
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── api/            # API接口定义
│   │   ├── components/     # Vue组件
│   │   │   ├── AmapView.vue         # 高德地图组件
│   │   │   └── DayPlanDetail.vue    # 单日行程详情组件
│   │   ├── views/          # 页面组件
│   │   │   ├── Home.vue            # 首页（表单页）
│   │   │   ├── PlanDetail.vue      # 行程详情页
│   │   │   └── TripMapView.vue     # 旅行地图视图
│   │   ├── router/         # 路由配置
│   │   ├── types/          # TypeScript类型定义
│   │   ├── App.vue         # 根组件
│   │   └── main.ts         # 应用入口
│   ├── package.json        # 前端依赖
│   ├── vite.config.ts      # Vite配置
│   └── README.md           # 前端文档
└── README.md               # 项目总体文档（本文件）
```

## 🧠 核心组件

### 后端核心模块

#### 数据模型 (data_model.py)
定义了旅行计划相关的所有数据结构，包括：
- `Attraction`：景点信息
- `Meal`：餐饮信息
- `Hotel`：酒店信息
- `WeatherInfo`：天气信息
- `DayPlan`：单日行程
- `TripRequest`：旅行请求
- `TripPlan`：完整旅行计划

#### 多智能体系统 (main.py)
实现了基于LangChain的多智能体架构：
- 使用高德地图MCP工具获取地理信息
- 各个专家代理专注于特定任务
- 行程规划代理整合所有信息生成最终计划

#### 数据解析器 (parse_info.py)
负责解析来自不同代理的原始数据并转换为统一的数据模型。

### 前端核心功能

#### 1. 旅行规划表单
- 目的地城市输入
- 日期范围选择
- 旅行天数设置
- 交通方式选择
- 住宿偏好选择
- 旅行偏好多选
- 额外要求输入

#### 2. 行程详情展示
- 总体建议
- 预算明细（景点、住宿、餐饮、交通）
- 天气信息展示
- 每日行程详情
  - 景点信息（含地图定位）
  - 酒店信息（含地图定位）
  - 餐饮安排（含地图定位）
  - 天气信息

#### 3. 地图集成
- 使用高德地图展示位置信息
- 支持标记点展示
- 支持信息窗口
- 自动调整视野范围

## 📡 API接口

### POST /trip

创建旅行计划

**请求体**:
```json
{
  "city": "北京",
  "start_date": "2025-12-20",
  "end_date": "2025-12-22",
  "travel_days": 3,
  "transportation": "公共交通",
  "accommodation": "经济型",
  "preferences": ["历史文化", "美食"],
  "free_text_input": ""
}
```

**响应**: TripPlan 对象，包含完整的旅行计划信息

## 🔧 配置说明

### 后端环境变量

- `GAODE_API_KEY`：高德地图API密钥，用于获取地理位置相关信息
- `LLM_API_KEY`：大语言模型API密钥
- `LLM_MODEL_ID`：使用的LLM模型ID
- `LLM_BASE_URL`：LLM服务的基础URL

### 前端环境变量

- `VITE_AMAP_KEY`：高德地图Web服务API密钥，用于前端地图展示
- `VITE_API_BASE_URL`：后端API服务地址（默认：http://localhost:8000）

### 开发代理配置

开发环境下，Vite 会将 `/api` 请求代理到后端服务（默认 http://localhost:8000）。配置在 `frontend/vite.config.ts` 中：

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

## 📊 输出示例

系统会生成两种格式的旅行手册：
1. **HTML格式**：交互式网页，包含丰富的视觉元素和布局
2. **PNG格式**：便于分享的图片版本

前端界面提供：
- 交互式行程详情页面
- 地图可视化展示
- 预算明细表格
- 每日行程时间表

## 🛣 路由说明

前端路由配置：

- `/` - 首页（旅行规划表单）
- `/plan/:id?` - 行程详情页

## ⚠️ 注意事项

1. **API 超时设置**: 由于后端处理时间较长（约5-10分钟），前端Axios超时时间设置为10分钟
2. **高德地图密钥**: 必须配置有效的高德地图API密钥才能正常使用地图功能
3. **后端服务**: 确保后端服务已启动并运行在 http://localhost:8000
4. **数据存储**: 前端行程详情数据使用 `sessionStorage` 临时存储，页面刷新后会丢失

## 🌐 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 🚀 生产部署

### 构建前端

```bash
cd frontend
npm run build
```

构建产物将输出到 `frontend/dist` 目录

### 预览生产构建

```bash
cd frontend
npm run preview
```

### 部署后端

可以使用以下方式部署后端服务：

```bash
# 使用gunicorn（推荐生产环境）
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# 或使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

本项目采用MIT许可证。

