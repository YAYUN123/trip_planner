import os
import asyncio
from typing import Any, List, Union

from fastapi import FastAPI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
import json
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Playwright
from data_model import *
from parse_info import parse_attraction_data, parse_weather_data, parse_hotel_data, parse_meal_data
import math


def haversine_distance(location1, location2):
    """
    计算两个经纬度点之间的距离（单位：米）
    """
    lat1, lon1 = location1.split(",")
    lat2, lon2 = location2.split(",")

    # 将经纬度转换为弧度
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # 计算差值
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine公式
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    # 地球半径（平均半径，单位：米）
    earth_radius = 6371000

    # 计算距离
    distance = earth_radius * c

    return distance


load_dotenv()

PLANNER_AGENT_SYSTEM_PROMPT = """你是行程规划专家。你的任务是根据景点信息和天气信息,生成详细的旅行计划。

请严格按照以下JSON格式返回旅行计划:
```json
{
  "city": "城市名称",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "第1天行程概述",
      "transportation": "交通方式",
      "accommodation": "住宿类型",
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
          "opentime": "景点的开放时间",
          "description": "景点详细描述",
          "category": "景点类别",
          "ticket_price": 60
        }
      ],
      "meals": [
        {"type": "breakfast", "name": "早餐推荐", "description": "早餐描述", "estimated_cost": 30},
        {"type": "lunch", "name": "午餐推荐", "description": "午餐描述", "estimated_cost": 50},
        {"type": "dinner", "name": "晚餐推荐", "description": "晚餐描述", "estimated_cost": 80}
      ]
    }
  ],
  "weather_info": [
    {
      "date": "YYYY-MM-DD",
      "day_weather": "晴",
      "night_weather": "多云",
      "day_temp": 25,
      "night_temp": 15,
      "wind_direction": "南风",
      "wind_power": "1-3级"
    }
  ],
  "overall_suggestions": "总体建议",
  "budget": {
    "total_attractions": 180,
    "total_hotels": 1200,
    "total_meals": 480,
    "total_transportation": 200,
    "total": 2060
  }
}
```

**重要提示:**
1. weather_info数组必须包含每一天的天气信息
2. 温度必须是纯数字(不要带°C等单位)
3. 每天安排2-3个景点
4. 考虑景点之间的距离和游览时间
5. 每天必须包含早中晚三餐
6. 提供实用的旅行建议
7. **必须包含预算信息**:
   - 景点门票价格(ticket_price)
   - 餐饮预估费用(estimated_cost)
   - 酒店预估费用(estimated_cost)
   - 预算汇总(budget)包含各项总费用
"""

def parse_messages(messages: List[Any]) -> None:
    """
    解析消息列表，打印 HumanMessage、AIMessage 和 ToolMessage 的详细信息

    Args:
        messages: 包含消息的列表，每个消息是一个对象
    """
    print("=== 消息解析结果 ===")
    for idx, msg in enumerate(messages, 1):
        print(f"\n消息 {idx}:")
        # 获取消息类型
        msg_type = msg.__class__.__name__
        print(f"类型: {msg_type}")
        # 提取消息内容
        content = getattr(msg, 'content', '')
        print(f"内容: {content if content else '<空>'}")
        # 处理附加信息
        additional_kwargs = getattr(msg, 'additional_kwargs', {})
        if additional_kwargs:
            print("附加信息:")
            for key, value in additional_kwargs.items():
                if key == 'tool_calls' and value:
                    print("  工具调用:")
                    for tool_call in value:
                        print(f"    - ID: {tool_call['id']}")
                        print(f"      函数: {tool_call['function']['name']}")
                        print(f"      参数: {tool_call['function']['arguments']}")
                else:
                    print(f"  {key}: {value}")
        # 处理 ToolMessage 特有字段
        if msg_type == 'ToolMessage':
            tool_name = getattr(msg, 'name', '')
            tool_call_id = getattr(msg, 'tool_call_id', '')
            print(f"工具名称: {tool_name}")
            print(f"工具调用 ID: {tool_call_id}")
        # 处理 AIMessage 的工具调用和元数据
        if msg_type == 'AIMessage':
            tool_calls = getattr(msg, 'tool_calls', [])
            if tool_calls:
                print("工具调用:")
                for tool_call in tool_calls:
                    print(f"  - 名称: {tool_call['name']}")
                    print(f"    参数: {tool_call['args']}")
                    print(f"    ID: {tool_call['id']}")
            # 提取元数据
            metadata = getattr(msg, 'response_metadata', {})
            if metadata:
                print("元数据:")
                token_usage = metadata.get('token_usage', {})
                print(f"  令牌使用: {token_usage}")
                print(f"  模型名称: {metadata.get('model_name', '未知')}")
                print(f"  完成原因: {metadata.get('finish_reason', '未知')}")
        # 打印消息 ID
        msg_id = getattr(msg, 'id', '未知')
        print(f"消息 ID: {msg_id}")
        print("-" * 50)

async def get_tools():
    print("  - 创建共享MCP工具...")
    gaode_api_key = os.getenv("GAODE_API_KEY")
    mcp_client = MultiServerMCPClient({
        # 高德地图MCP Server
        "amap-amap-sse": {
            "url": f"https://mcp.amap.com/sse?key={gaode_api_key}",
            "transport": "sse",
        }
    })

    # 从MCP Server中获取可提供使用的全部工具
    tools = await mcp_client.get_tools()
    # print(type(tools))
    return tools


class MultiAgentTripPlanner:
    """多智能体旅行规划系统"""

    def __init__(self, tools):
        """初始化多智能体系统"""
        print("🔄 开始初始化多智能体旅行规划系统...")
        try:
            self.llm = init_chat_model(
                model=os.getenv("LLM_MODEL_ID"),
                api_key=os.getenv("LLM_API_KEY"),
                base_url="https://api.deepseek.com/v1",
                temperature=0,
                max_tokens=8000
            )

            # 定义系统消息，指导如何使用工具
            system_message = SystemMessage(content=(
                "你是一个AI助手，使用高德地图工具获取信息。"
            ))
            print("  - 创建景点搜索Agent...")
            self.attraction_agent = create_react_agent(
                name="景点搜索专家",
                model=self.llm,
                prompt=system_message,
                tools=tools
            )

            # 创建天气查询Agent
            print("  - 创建天气查询Agent...")
            self.weather_agent = create_react_agent(
                name="天气查询专家",
                model=self.llm,
                prompt=system_message,
                tools=tools
            )

            # 创建酒店推荐Agent
            print("  - 创建酒店推荐Agent...")
            self.hotel_agent = create_react_agent(
                name="酒店推荐专家",
                model=self.llm,
                prompt=system_message,
                tools=tools
            )

            # 创建吃饭地方推荐Agent
            print("  - 创建美食推荐Agent...")
            self.meal_agent = create_react_agent(
                name="美食推荐专家",
                model=self.llm,
                prompt=system_message,
                tools=tools
            )

            # 创建行程规划Agent(不需要工具)
            print("  - 创建行程规划Agent...")
            self.planner_agent = create_react_agent(
                name="行程规划专家",
                model=self.llm,
                prompt=PLANNER_AGENT_SYSTEM_PROMPT,
                tools=[]
            )

            print("   - 创建精美旅行手册Agent...")
            self.create_travel_guide_agent = create_react_agent(
                name="创建精美手册专家",
                model=self.llm,
                prompt="将下面这段json数据，使用html制作成网页，当做一个旅行助手的精美手册，只输出html代码，不要输出其他的内容。",
                tools=[]
            )

            print(f"✅ 多智能体系统初始化成功")
            print(f"   景点搜索Agent: {len(tools)} 个工具")
            print(f"   天气查询Agent: {len(tools)} 个工具")
            print(f"   酒店推荐Agent: {len(tools)} 个工具")
        except Exception as e:
            print(f"❌ 多智能体系统初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    async def plan_trip(self, request: TripRequest) -> TripPlan:
        """
        使用多智能体协作生成旅行计划

        Args:
            request: 旅行请求

        Returns:
            旅行计划
        """
        try:
            print(f"\n{'='*60}")
            print(f"🚀 开始多智能体协作规划旅行...")
            print(f"目的地: {request.city}")
            print(f"日期: {request.start_date} 至 {request.end_date}")
            print(f"天数: {request.travel_days}天")
            print(f"偏好: {', '.join(request.preferences) if request.preferences else '无'}")
            print(f"{'='*60}\n")

            # 步骤1: 景点搜索Agent搜索景点
            print("📍 步骤1: 搜索景点...")
            attraction_query = self._build_attraction_query(request)
            attraction_response = await self.attraction_agent.ainvoke(
                input={"messages": [HumanMessage(content=attraction_query)]},
                # stream_mode="values"
            )
            attraction_response_messages = attraction_response['messages']
            # attraction_response = attraction_response_messages[1].content
            parse_messages(attraction_response_messages)
            attraction_response = parse_attraction_data(attraction_response_messages)
            print(f"景点搜索结果: {attraction_response}\n")
            assert attraction_response != [], f"景点搜索结果:[]，没有搜索到景点结果"

            # 步骤2: 天气查询Agent查询天气
            print("🌤️  步骤2: 查询天气...")
            weather_query = f"帮我查询{request.city}的天气信息"
            weather_response = await self.weather_agent.ainvoke(
                {"messages": [{'role': 'user', 'content': weather_query}]})
            weather_response_messages = weather_response["messages"]
            # weather_response = weather_response["messages"][1].content
            weather_response = parse_weather_data(weather_response_messages, request.start_date, request.end_date)
            print(f"天气查询结果: {weather_response}...\n")
            # parse_messages(weather_response_messages)
            assert weather_response != [], f"天气搜索结果:[]，没有搜索到天气结果"

            # 步骤3: 酒店推荐Agent搜索酒店
            print("🏨 步骤3: 搜索酒店...")
            first_attraction_name = attraction_response[0].name
            first_attraction_location = attraction_response[0].location
            hotel_query = f"请搜索{request.city}的{first_attraction_name}周围1公里的{request.accommodation}酒店，然后挑选已经搜索出来的{request.travel_days-1}个酒店的详情信息"
            hotel_response = await self.hotel_agent.ainvoke(
                {"messages": [{'role': 'user', 'content': hotel_query}]})
            hotel_response_messages = hotel_response["messages"]
            # hotel_response = hotel_response["messages"][1].content
            hotel_response = parse_hotel_data(hotel_response_messages)

            # hotel_id2location = {hotel["id"]: hotel["location"] for hotel in hotel_response}
            # distances = {hotel["id"]: haversine_distance(hotel["location"], first_attraction_location)
            #              for hotel in hotel_response}
            # min_distance_hotel_id = min(distances, key=distances.get)

            print(f"酒店搜索结果: {hotel_response}...\n")
            # parse_messages(hotel_response_messages)
            assert hotel_response != [], f"酒店搜索结果:[]，没有搜索到酒店结果"

            # # 步骤4: 美食推荐Agent搜索美食
            # print("🏨 步骤4: 搜索美食...")
            # meal_query = f"帮我搜索{request.city}的{request.accommodation}美食。"
            # meal_response = await self. meal_agent.ainvoke(
            #     {"messages": [{'role': 'user', 'content': meal_query}]})
            # meal_response_messages = meal_response["messages"]
            # meal_response = parse_meal_data(meal_response_messages)
            # print(f"美食搜索结果: {meal_response}...\n")

            # 步骤5: 行程规划Agent整合信息生成计划
            print("📋 步骤5: 生成行程计划...")
            planner_query = self._build_planner_query(request,
                                                      attraction_response,
                                                      weather_response,
                                                      hotel_response,
                                                      )
            print(f"{'=' * 60}")
            print(f"✅ 汇总信息: {planner_query}\n")
            print(f"{'=' * 60}\n")
            planner_response = self.planner_agent.invoke(
                {"messages":[{'role': 'user', 'content': planner_query}]})
            planner_response = planner_response["messages"][1].content
            print(f"行程规划结果: {planner_response}...\n")

            # 解析最终计划
            print("📲 步骤6: 生成html代码...")
            trip_plan = self._parse_response(planner_response, "```json", request)
            travel_guider_query = f"数据内容:\n{trip_plan}"
            travel_guider_response = self.create_travel_guide_agent.invoke(
                {"messages": [{'role': 'user', 'content': travel_guider_query}]})
            html_content = travel_guider_response["messages"][-1].content
            print(f"html_content: {html_content}\n")
            html_code = self._parse_response(html_content, "```html", request)
            output_file_name = f"{request.city}旅行手册.html"
            self._create_html(html_code, output_file_name)

            print("✅ 步骤7: 制作精美手册...")
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page(viewport={'width': 1280, 'height': 800})
                file_path = os.path.abspath(output_file_name)
                await page.goto(f'file:{file_path}')  # 或 http://...
                await page.screenshot(path=file_path.replace("html", "png"), full_page=True)  # full_page=True 自动滚到到底
                await browser.close()

            print(f"{'='*60}")
            print(f"✅ 旅行计划生成完成!")
            print(f"{'='*60}\n")

            return trip_plan

        except Exception as e:
            print(f"❌ 生成旅行计划失败: {str(e)}")
            import traceback
            traceback.print_exc()
            # return self._create_fallback_plan(request)

    def _create_fallback_plan(self, request: TripRequest) -> TripPlan:
        """创建备用计划(当Agent失败时)"""
        from datetime import datetime, timedelta

        # 解析日期
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")

        # 创建每日行程
        days = []
        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)

            day_plan = DayPlan(
                date=current_date.strftime("%Y-%m-%d"),
                day_index=i,
                description=f"第{i + 1}天行程",
                transportation=request.transportation,
                accommodation=request.accommodation,
                attractions=[
                    Attraction(
                        name=f"{request.city}景点{j + 1}",
                        address=f"{request.city}市",
                        location=Location(longitude=116.4 + i * 0.01 + j * 0.005, latitude=39.9 + i * 0.01 + j * 0.005),
                        visit_duration=120,
                        description=f"这是{request.city}的著名景点",
                        category="景点"
                    )
                    for j in range(2)
                ],
                meals=[
                    Meal(type="breakfast", name=f"第{i + 1}天早餐", description="当地特色早餐"),
                    Meal(type="lunch", name=f"第{i + 1}天午餐", description="午餐推荐"),
                    Meal(type="dinner", name=f"第{i + 1}天晚餐", description="晚餐推荐")
                ]
            )
            days.append(day_plan)

        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=[],
            overall_suggestions=f"这是为您规划的{request.city}{request.travel_days}日游行程,建议提前查看各景点的开放时间。"
        )

    @staticmethod
    def _build_attraction_query(request: TripRequest):
        """构建景点搜索查询 - 直接包含工具调用"""
        if request.preferences:
            # 只取第一个偏好作为关键词
            keywords = request.preferences[0]
        else:
            keywords = "景点"

        # 直接返回工具调用格式
        # query = f"帮我搜索{request.city}的{keywords}相关景点"
        query = f"帮我搜一下{request.city}的{keywords}相关景点，然后挑选已经搜索出来的6个景点的详情信息"
        return query

    @staticmethod
    def _build_planner_query(request, attraction_response, weather_response, hotel_response):
        query = f"""
请根据以下信息生成{request.city}的{request.travel_days}天计划

**基本信息:**
- 城市: {request.city}
- 日期: {request.start_date} 至 {request.end_date}
- 天数: {request.travel_days}天
- 交通方式: {request.transportation}
- 住宿: {request.accommodation}
- 偏好: {', '.join(request.preferences) if request.preferences else '无'}

**景点信息:**
{attraction_response}

**天气信息:**
{weather_response}

**酒店信息:**
{hotel_response}

请生成详细的旅行计划,包括每天的景点安排、餐饮推荐、住宿信息和预算明细。
"""
        return query

    def _parse_response2(self, response: str, data_type: str, request: TripRequest) -> Union[TripPlan, str]:
        """
        解析Agent响应

        Args:
            response: Agent响应文本
            request: 原始请求

        Returns:
            旅行计划
        """
        try:
            # 尝试从响应中提取JSON/html
            # 查找JSON/html代码块
            if data_type in response:
                start = response.find(data_type) + 7
                end = response.find("```", start)
                str_content = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                str_content = response[start:end].strip()
            elif "{" in response and "}" in response:
                # 直接查找JSON对象
                start = response.find("{")
                end = response.rfind("}") + 1
                str_content = response[start:end]
            elif "<!DOCTYPE html>" in response and "</html>" in response:
                # 直接查找html代码
                start = response.find("<!DOCTYPE html>")
                end = response.rfind("</html>") + 1
                str_content = response[start:end]
            else:
                raise ValueError("响应中未找到JSON数据")

            # 解析JSON
            if data_type == "```json":
                data = json.loads(str_content)

                # 转换为TripPlan对象
                trip_plan = TripPlan(**data)

                return trip_plan
            else:
                return str_content

        except Exception as e:
            print(f"⚠️  解析响应失败: {str(e)}")
            # print(f"   将使用备用方案生成计划")
            # return self._create_fallback_plan(request)

    def _parse_response(self, response: str, data_type: str, request: TripRequest) -> Union[TripPlan, str]:
        """
        解析Agent响应
        
        Args:
            response: Agent响应文本
            data_type: 数据类型 ("```json" 或 "```html")
            request: 原始请求
            
        Returns:
            旅行计划或HTML字符串
            
        Raises:
            ValueError: 当无法解析响应时
        """
        try:
            # 输入验证
            if not isinstance(response, str):
                raise ValueError("响应必须是字符串类型")
                
            # 尝试从响应中提取指定类型的代码块
            if data_type in response:
                start = response.find(data_type) + len(data_type)
                # 寻找下一个 ``` 标记
                end = response.find("```", start)
                if end == -1:
                    # 如果找不到结束标记，尝试提取到最后
                    str_content = response[start:].strip()
                else:
                    str_content = response[start:end].strip()
            elif "```" in response:
                # 尝试提取任意代码块
                start = response.find("```") + 3
                # 跳过可能的语言标识符（如 json, html 等）
                start = response.find("\n", start) + 1 if "\n" in response[start:start+10] else start
                end = response.find("```", start)
                str_content = response[start:end].strip() if end != -1 else response[start:].strip()
            elif data_type == "```json" and "{" in response and "}" in response:
                # 直接查找JSON对象
                start = response.find("{")
                end = response.rfind("}") + 1
                str_content = response[start:end]
            elif data_type == "```html" and "<!DOCTYPE html>" in response and "</html>" in response:
                # 直接查找html代码
                start = response.find("<!DOCTYPE html>")
                end = response.rfind("</html>") + 7  # "</html>" 长度为 7
                str_content = response[start:end]
            else:
                raise ValueError(f"响应中未找到{data_type}数据")
            
            # 根据数据类型解析内容
            if data_type == "```json":
                data = json.loads(str_content)
                # 转换为TripPlan对象
                return TripPlan(**data)
            if data_type == "```html" and "<!DOCTYPE html>" in str_content and "</html>" in str_content:
                return str_content
            else:
                raise ValueError(f"无法解析{data_type}数据, 不是完整的可执行的代码")
                
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON解析失败: {str(e)}")
            raise ValueError(f"无法解析JSON数据: {str(e)}")
        except Exception as e:
            print(f"⚠️  解析响应失败: {str(e)}")
            raise ValueError(f"解析响应时发生错误: {str(e)}")

    def _create_html(self, html_code, output_file_name):
        try:
            with open(output_file_name, "w", encoding="utf-8") as file:
                file.write(html_code)
            print(f"成功生成 HTML 文件: {output_file_name}")
        except IOError as e:
            print(f"写入文件时发生错误: {e}")

app = FastAPI()
@app.post("/trip", response_model=TripPlan)
async def read_root(request: TripRequest):
    tools = await get_tools()
    multi_agent_trip_planner = MultiAgentTripPlanner(tools)
    trip_plan = await multi_agent_trip_planner.plan_trip(request)
    print(trip_plan)
    # trip_plan = TripPlan(
    #     city="杭州",
    #     start_date="2026-01-01",
    #     end_date="2026-01-03",
    #     overall_suggestions="别来"
    # )
    return trip_plan