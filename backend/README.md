# 旅行规划助手 (Trip Planner Backend)

一个基于AI的智能旅行规划系统后端服务，能够根据用户需求自动生成详细的旅行计划，包括景点推荐、天气信息、住宿安排、餐饮建议和预算估算。

## 🌟 功能特点

- **智能景点推荐**：基于用户偏好和目的地自动推荐合适的景点，支持多偏好标签筛选
- **天气信息查询**：获取旅行期间的详细天气预报，包括白天/夜间天气、温度、风向风力
- **住宿安排建议**：根据景点位置智能聚类，推荐附近合适的酒店住宿
- **餐饮计划推荐**：提供每日三餐的推荐和预算估算
- **个性化行程规划**：根据时间和景点位置优化行程安排，考虑景点间距离和游览时间
- **预算估算**：提供详细的费用预算，包括景点门票、住宿、餐饮和交通
- **智能景点聚类**：使用贪心算法对景点进行地理位置聚类，优化酒店推荐

## 🛠 技术架构

本项目采用多智能体架构，利用多个专门的AI代理协同工作：

### 核心组件

- **景点搜索专家 (Attraction Agent)**：负责搜索和筛选目标城市的景点，支持偏好标签筛选
- **天气查询专家 (Weather Agent)**：获取旅行期间的详细天气信息
- **酒店推荐专家 (Hotel Agent)**：基于景点聚类结果，推荐附近合适的住宿选择
- **美食推荐专家 (Meal Agent)**：提供每日三餐的餐饮建议
- **行程规划专家 (Planner Agent)**：整合所有信息生成最优旅行计划，包含详细预算
- **手册制作专家 (Travel Guide Agent)**：将旅行计划转化为精美的HTML手册（可选功能）

### 技术栈

- **Web框架**：FastAPI
- **AI框架**：LangChain + LangChain MCP Adapters
- **LLM支持**：支持 DeepSeek、OpenAI 等兼容 OpenAI API 的模型
- **地图服务**：高德地图 MCP Server
- **数据处理**：Pydantic 数据验证
- **地理计算**：NumPy（Haversine 公式计算距离）

## 🚀 快速开始

### 环境要求

- Python 3.12+
- 高德地图API密钥（获取指南：https://amap.apifox.cn/doc-537183）
- LLM API密钥（DeepSeek/OpenAI 等）

### 安装步骤

1. **克隆项目仓库**：
   ```bash
   git clone https://github.com/YAYUN123/trip_planner.git
   cd trip_planner/backend
   ```

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
   
   主要依赖包括：
   - `fastapi`：Web框架
   - `langchain`、`langchain-core`：AI框架
   - `langchain-mcp-adapters`：MCP工具适配器
   - `pydantic`：数据验证
   - `python-dotenv`：环境变量管理
   - `uvicorn`：ASGI服务器
   - `playwright`：HTML转PNG（可选）

3. **配置环境变量**：
   
   在项目根目录创建 `.env` 文件，配置以下API密钥：
   ```env
   GAODE_API_KEY="your_amap_api_key"
   LLM_API_KEY="your_llm_api_key"
   LLM_MODEL_ID="your_preferred_model"  # 如: deepseek-chat
   LLM_BASE_URL="your_llm_base_url"     # 如: https://api.deepseek.com
   ```

4. **运行应用**：
   ```bash
   uvicorn main:app --reload
   ```
   
   服务启动后，API文档可访问：`http://localhost:8000/docs`

## 📡 API接口

### 提交旅行计划请求

**端点**：`POST /trip`

**请求体示例**：
```json
{
  "city": "北京",
  "start_date": "2025-12-20",
  "end_date": "2025-12-22",
  "travel_days": 3,
  "transportation": "公共交通",
  "accommodation": "经济型",
  "preferences": ["历史文化", "美食"],
  "free_text_input": "希望行程不要太紧张"
}
```

**请求参数说明**：
- `city` (string, 必需)：目的地城市名称
- `start_date` (string, 必需)：开始日期，格式 YYYY-MM-DD
- `end_date` (string, 必需)：结束日期，格式 YYYY-MM-DD
- `travel_days` (int, 必需)：旅行天数，范围 1-30
- `transportation` (string, 必需)：交通方式，如"公共交通"、"自驾"等
- `accommodation` (string, 必需)：住宿偏好，如"经济型"、"豪华型"等
- `preferences` (array, 可选)：旅行偏好标签列表，如["历史文化", "美食", "自然风光"]
- `free_text_input` (string, 可选)：额外要求或说明

**响应示例**：
```json
{
  "city": "北京",
  "start_date": "2025-12-20",
  "end_date": "2025-12-22",
  "days": [
    {
      "date": "2025-12-20",
      "day_index": 0,
      "description": "第1天行程概述",
      "transportation": "公共交通",
      "accommodation": "经济型",
      "hotel": {
        "name": "酒店名称",
        "address": "酒店地址",
        "location": {"longitude": 116.397128, "latitude": 39.916527},
        "price_range": "300-500元",
        "rating": "4.5",
        "distance": "距离景点2公里",
        "type": "经济型酒店",
        "estimated_cost": 400
      },
      "attractions": [
        {
          "name": "景点名称",
          "address": "详细地址",
          "location": {"longitude": 116.397128, "latitude": 39.916527},
          "opentime": "08:00-18:00",
          "description": "景点详细描述",
          "category": "历史文化",
          "rating": 4.8,
          "image_url": "https://...",
          "ticket_price": 60
        }
      ],
      "meals": [
        {
          "type": "breakfast",
          "name": "早餐推荐",
          "address": "地址",
          "location": {"longitude": 116.397128, "latitude": 39.916527},
          "description": "早餐描述",
          "estimated_cost": 30
        }
      ]
    }
  ],
  "weather_info": [
    {
      "date": "2025-12-20",
      "day_weather": "晴",
      "night_weather": "多云",
      "day_temp": 25,
      "night_temp": 15,
      "wind_direction": "南风",
      "wind_power": "1-3级"
    }
  ],
  "overall_suggestions": "总体建议和注意事项",
  "budget": {
    "total_attractions": 180,
    "total_hotels": 1200,
    "total_meals": 480,
    "total_transportation": 200,
    "total": 2060
  }
}
```

**注意**：生成完整旅行计划通常需要约 10 分钟，请耐心等待。

## 📁 项目结构

```
backend/
├── main.py              # 主程序入口，包含FastAPI服务和多智能体系统
├── data_model.py        # 数据模型定义（Pydantic模型）
├── parse_info.py        # 数据解析工具，解析Agent返回的原始数据
├── prompts.py           # 系统提示词定义
├── cluster.py           # 景点聚类算法（贪心算法，基于Haversine距离）
├── troubleshooting.py   # 故障排查工具（可选）
├── requirements.txt     # Python依赖包列表
├── .env                 # 环境变量配置文件（需自行创建）
├── .gitignore          # Git忽略文件配置
└── README.md           # 项目说明文档
```

## 🧠 核心组件详解

### 1. 数据模型 (data_model.py)

定义了旅行计划相关的所有数据结构，使用 Pydantic 进行数据验证：

- `Location`：地理位置坐标（经纬度）
- `Attraction`：景点信息（名称、地址、位置、开放时间、描述、评分、票价等）
- `Meal`：餐饮信息（类型、名称、地址、位置、描述、预估费用）
- `Hotel`：酒店信息（名称、地址、位置、价格范围、评分、距离、类型、预估费用）
- `WeatherInfo`：天气信息（日期、白天/夜间天气、温度、风向、风力）
- `DayPlan`：单日行程（日期、景点列表、餐饮安排、酒店信息等）
- `Budget`：预算信息（各项费用汇总）
- `TripRequest`：旅行请求（用户输入）
- `TripPlan`：完整旅行计划（最终输出）

### 2. 多智能体系统 (main.py)

实现了基于 LangChain 的多智能体架构：

- **MultiAgentTripPlanner**：多智能体规划器主类
  - 初始化各个专家Agent
  - 协调各Agent协作完成旅行规划
  - 处理错误重试机制

- **工作流程**：
  1. 景点搜索：根据用户偏好搜索并筛选景点
  2. 天气查询：获取旅行期间的天气信息
  3. 景点聚类：使用贪心算法对景点进行地理位置聚类
  4. 酒店推荐：基于聚类结果，为每个聚类中心推荐附近酒店
  5. 美食推荐：推荐每日三餐的餐饮地点
  6. 行程规划：整合所有信息，生成详细的旅行计划和预算

### 3. 数据解析器 (parse_info.py)

负责解析来自不同Agent的原始数据并转换为统一的数据模型：

- `parse_attraction_data()`：解析景点数据
- `parse_weather_data()`：解析天气数据
- `parse_hotel_data()`：解析酒店数据
- `parse_meal_data()`：解析餐饮数据
- `parse_messages()`：通用消息解析工具

### 4. 景点聚类算法 (cluster.py)

实现基于 Haversine 公式的贪心聚类算法：

- `haversine_distance()`：计算两点间球面距离
- `build_distance_matrix()`：构建距离矩阵
- `greedy_cluster()`：贪心聚类，每组最多3个点，优化酒店推荐位置

### 5. 提示词管理 (prompts.py)

定义各Agent的系统提示词，特别是行程规划Agent的详细JSON格式要求。

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `GAODE_API_KEY` | 高德地图API密钥，用于获取地理位置相关信息 | `your_amap_api_key` |
| `LLM_API_KEY` | 大语言模型API密钥 | `your_llm_api_key` |
| `LLM_MODEL_ID` | 使用的LLM模型ID | `deepseek-chat` |
| `LLM_BASE_URL` | LLM服务的基础URL | `https://api.deepseek.com` |

### API密钥获取

- **高德地图API**：访问 https://amap.apifox.cn/doc-537183 获取密钥
- **LLM API**：根据使用的服务商（DeepSeek/OpenAI等）获取相应密钥

## 🐛 故障排查

如果遇到问题，可以：

1. 检查环境变量配置是否正确
2. 确认API密钥是否有效
3. 查看控制台输出的详细日志
4. 使用 `troubleshooting.py` 进行诊断（如果存在）

## 📊 输出说明

系统会生成结构化的旅行计划JSON，包含：

1. **每日行程**：景点安排、餐饮推荐、酒店信息
2. **天气信息**：每日详细天气预报
3. **预算明细**：景点门票、住宿、餐饮、交通等各项费用
4. **总体建议**：实用的旅行建议和注意事项

## ⚠️ 注意事项

1. **API调用时间**：完整规划通常需要约 10 分钟，请耐心等待
2. **重试机制**：系统内置重试机制，失败会自动重试（最多2次）
3. **数据准确性**：所有地理位置和价格信息来自高德地图API，请以实际为准
4. **模型要求**：建议使用支持长文本输出的LLM模型（如 DeepSeek）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 📄 许可证

本项目采用 MIT 许可证。
