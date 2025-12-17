import os
from typing import Any, List, Union
from fastapi import FastAPI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
import json
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Playwright
from data_model import *
from parse_info import parse_attraction_data, parse_weather_data, parse_hotel_data, parse_meal_data, parse_messages
from prompts import PLANNER_AGENT_SYSTEM_PROMPT
from cluster import greedy_cluster

load_dotenv()


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
                base_url=os.getenv("LLM_BASE_URL"),
                temperature=0,
                max_tokens=8000
            )

            # 定义系统消息，指导如何使用工具
            system_message = SystemMessage(content=(
                "你是一个AI助手，使用高德地图工具获取信息。"
            ))
            print("  - 创建景点搜索Agent...")
            self.attraction_agent = create_agent(
                name="景点搜索专家",
                model=self.llm,
                system_prompt=system_message,
                tools=tools
            )

            # 创建天气查询Agent
            print("  - 创建天气查询Agent...")
            self.weather_agent = create_agent(
                name="天气查询专家",
                model=self.llm,
                system_prompt=system_message,
                tools=tools
            )

            # 创建酒店推荐Agent
            print("  - 创建酒店推荐Agent...")
            self.hotel_agent = create_agent(
                name="酒店推荐专家",
                model=self.llm,
                system_prompt=system_message,
                tools=tools
            )

            # 创建吃饭地方推荐Agent
            print("  - 创建美食推荐Agent...")
            self.meal_agent = create_agent(
                name="美食推荐专家",
                model=self.llm,
                system_prompt=system_message,
                tools=tools
            )

            # 创建行程规划Agent(不需要工具)
            print("  - 创建行程规划Agent...")
            self.planner_agent = create_agent(
                name="行程规划专家",
                model=self.llm,
                system_prompt=PLANNER_AGENT_SYSTEM_PROMPT,
                tools=[]
            )

            print("   - 创建精美旅行手册Agent...")
            self.create_travel_guide_agent = create_agent(
                name="创建精美手册专家",
                model=self.llm,
                system_prompt="将下面这段json数据，使用html制作成网页，当做一个旅行助手的精美手册，只输出html代码，不要输出其他的内容。",
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
            for single_attraction in attraction_response:
                print(f"景点搜索结果: {single_attraction}\n")
            assert attraction_response != [], f"景点搜索结果:[]，没有搜索到景点结果"

            # 步骤2: 天气查询Agent查询天气
            print("🌤️  步骤2: 查询天气...")
            weather_query = f"帮我查询{request.city}的天气信息"
            weather_response = await self.weather_agent.ainvoke(
                {"messages": [{'role': 'user', 'content': weather_query}]})
            weather_response_messages = weather_response["messages"]
            # weather_response = weather_response["messages"][1].content
            weather_response = parse_weather_data(weather_response_messages, request.start_date, request.end_date)
            for single_weather in weather_response:
                print(f"天气查询结果: {single_weather}\n")
            # parse_messages(weather_response_messages)
            assert weather_response != [], f"天气搜索结果:[]，没有搜索到天气结果"

            # 步骤3: 酒店推荐Agent搜索酒店
            print("🏨 步骤3: 搜索酒店...")
            # 根据景点经纬度，寻找附近的酒店
            locations2name = dict()
            attraction_locations = []
            for single_attraction in attraction_response:
                location = single_attraction.location
                attraction_locations.append([location.longitude, location.latitude])

                location = ','.join([str(location.longitude), str(location.latitude)])
                locations2name[location] = single_attraction.name
            clusters = greedy_cluster(attraction_locations)

            # 中心景点
            central_attraction_names = []
            for cluster in clusters:
                longitude, latitude = attraction_locations[cluster[0]]
                location = ','.join([str(longitude), str(latitude)])
                central_attraction_names.append(locations2name[location])

            hotel_response = []
            for central_attraction_name in central_attraction_names:
                hotel_query = self._build_hotel_query(request, central_attraction_name)
                single_hotel_response = await self.hotel_agent.ainvoke(
                    {"messages": [{'role': 'user', 'content': hotel_query}]})
                single_hotel_response_messages = single_hotel_response["messages"]
                # single_hotel_response = single_hotel_response["messages"][1].content
                single_hotel_response = parse_hotel_data(single_hotel_response_messages,
                                                         central_attraction_name,
                                                         request.accommodation)[0]
                print(f"酒店搜索结果: {single_hotel_response}\n")
                hotel_response.append(single_hotel_response)
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
        query = f"帮我搜一下{request.city}的{keywords}相关景点，然后挑选已经搜索出来的{request.travel_days*3}个景点的详情信息"
        return query

    @staticmethod
    def _build_hotel_query(request, central_attraction_name):
        return f"请搜索{request.city}的{central_attraction_name}周围1公里的{request.accommodation}酒店，然后挑选已经搜索出来的1个酒店的详情信息"


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

请生成详细的旅行计划,包括每天的景点安排、餐饮推荐、住宿信息、天气情况和预算明细，必须按照上述信息生成，不能随意捏造数据！！！。
"""
        if request.free_text_input:
            query += f"\n**额外要求:** {request.free_text_input}"

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