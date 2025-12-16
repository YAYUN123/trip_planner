# 旅行规划助手 (Trip Planner)

一个基于AI的智能旅行规划系统，能够根据用户需求自动生成详细的旅行计划，包括景点推荐、天气信息、住宿安排、餐饮建议和预算估算。

## 🌟 功能特点

- **智能景点推荐**：基于用户偏好和目的地自动推荐合适的景点
- **天气信息查询**：获取旅行期间的详细天气预报
- **住宿安排建议**：推荐符合用户偏好的酒店住宿
- **餐饮计划推荐**：提供每日三餐的推荐和预算
- **个性化行程规划**：根据时间和景点位置优化行程安排
- **预算估算**：提供详细的费用预算，包括景点门票、住宿、餐饮和交通
- **精美旅行手册**：自动生成HTML格式的可视化旅行手册和PNG图片

## 🛠 技术架构

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
- 高德地图API密钥(获取指南：https://amap.apifox.cn/doc-537183)
- LLM API密钥 (DeepSeek/OpenAI)

### 安装步骤

1. 克隆项目仓库：
   ```bash
   git clone https://github.com/YAYUN123/trip_planner.git
   cd trip_planner
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量：
   在 `.env` 文件中配置以下API密钥：
   ```
   GAODE_API_KEY=your_amap_api_key
   LLM_API_KEY=your_llm_api_key
   LLM_MODEL_ID=your_preferred_model
   LLM_BASE_URL=your_llm_base_url
   ```

4. 运行应用：
   ```bash
   uvicorn main:app --reload
   ```

### API接口

启动服务后，可以通过以下端点提交旅行计划请求：

```
POST /trip
```

请求示例：
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

## 📁 项目结构

```
trip_planner/
├── main2.py           # 主程序入口，包含FastAPI服务和多智能体系统
├── data_model.py      # 数据模型定义
├── parse_info.py      # 数据解析工具
├── .env               # 环境变量配置文件
├── 北京旅行手册.html    # 示例旅行手册(HTML格式)
├── 北京旅行手册.png    # 示例旅行手册(PNG格式)
├── 杭州旅行手册.html    # 示例旅行手册(HTML格式)
└── 杭州旅行手册.png    # 示例旅行手册(PNG格式)
```

## 🧠 核心组件

### 数据模型 (data_model.py)
定义了旅行计划相关的所有数据结构，包括：
- `Attraction`：景点信息
- `Meal`：餐饮信息
- `Hotel`：酒店信息
- `WeatherInfo`：天气信息
- `DayPlan`：单日行程
- `TripRequest`：旅行请求
- `TripPlan`：完整旅行计划

### 多智能体系统 (main2.py)
实现了基于LangChain的多智能体架构：
- 使用高德地图MCP工具获取地理信息
- 各个专家代理专注于特定任务
- 行程规划代理整合所有信息生成最终计划

### 数据解析器 (parse_info.py)
负责解析来自不同代理的原始数据并转换为统一的数据模型。

## 📊 输出示例

系统会生成两种格式的旅行手册：
1. **HTML格式**：交互式网页，包含丰富的视觉元素和布局
2. **PNG格式**：便于分享的图片版本

## 🔧 配置说明

### 环境变量
- `GAODE_API_KEY`：高德地图API密钥，用于获取地理位置相关信息
- `LLM_API_KEY`：大语言模型API密钥
- `LLM_MODEL_ID`：使用的LLM模型ID
- `LLM_BASE_URL`：LLM服务的基础URL

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

本项目采用MIT许可证。