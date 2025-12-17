import json
from datetime import date, timedelta
from typing import List, Any
from data_model import Attraction, Location, WeatherInfo, Hotel, Meal


def build_attraction(content: dict) -> Attraction:
    lon_str, lat_str = content["location"].split(",")
    ticket_price = 0 if content["cost"] == "" else int(content["cost"])
    return Attraction(
        name=content["name"],
        address=content["address"],
        location=Location(longitude=float(lon_str), latitude=float(lat_str)),
        opentime=content.get('opentime2', ''),  # 默认 60 分钟
        description=content.get("level", ""),  # 如无描述可留空
        category=content.get("type", ''),  # 默认
        rating=float(content.get("rating", 0)),
        image_url=content.get("photo", ""),
        ticket_price=ticket_price
    )


def parse_attraction_data(messages):
    attractions = []

    print("=== //消息解析结果// ===")
    for idx, msg in enumerate(messages, 1):
        # 获取消息类型
        msg_type = msg.__class__.__name__
        # 提取消息内容
        content = getattr(msg, 'content', '')
        """
        {
            "id": "B000A7O1CU",
            "name": "颐和园",
            "location": "116.275179,39.999617",
            "address": "新建宫门路19号",
            "business_area": "",
            "city": "北京市",
            "type": "风景名胜;风景名胜;世界遗产",
            "alias": "",
            "photo": "http://store.is.autonavi.com/showpic/a4b326f43a84d36b581d7f6e856fe858",
            "cost": "",
            "opentime2": "旺季:4月1日至10月31日:06:00-20:00(19:00停止进入)；淡季:11月1日至3月31日:06:30-19:00(18:00停止进入)",
            "level": "AAAAA",
            "rating": "4.9",
            "open_time": "",
            "ticket_ordering": "0"
        }
        """

        if msg_type != "ToolMessage":
            continue
        content = json.loads(content[0].get('text'))
        if content.get("location", ""):
            attractions.append(build_attraction(content))
    return attractions


def build_weather(content: dict) -> WeatherInfo:
    return WeatherInfo(
        date=content["date"],
        day_weather=content["dayweather"],
        night_weather=content["nightweather"],
        day_temp=content["daytemp"],
        night_temp=content["nighttemp"],
        wind_direction=content["daywind"],
        wind_power=content["daypower"]
    )


def get_dates_between_date(start_date, end_date):
    """使用date类获取日期"""
    start = date.fromisoformat(start_date)  # Python 3.7+
    end = date.fromisoformat(end_date)

    delta_days = (end - start).days
    dates = []

    for i in range(delta_days + 1):
        current_date = start + timedelta(days=i)
        dates.append(current_date.isoformat())

    return dates

def parse_weather_data(messages, start_date, end_date):
    weathers = []
    dates = get_dates_between_date(start_date, end_date)

    print("=== //消息解析结果// ===")
    for idx, msg in enumerate(messages, 1):
        # 获取消息类型
        msg_type = msg.__class__.__name__
        # 提取消息内容
        content = getattr(msg, 'content', '')

        """
        [{
            "date": "2025-12-15",
            "week": "1",
            "dayweather": "阴",
            "nightweather": "多云",
            "daytemp": "12",
            "nighttemp": "5",
            "daywind": "南",
            "nightwind": "南",
            "daypower": "1-3",
            "nightpower": "1-3",
            "daytemp_float": "12.0",
            "nighttemp_float": "5.0"
        }, {
            "date": "2025-12-16",
            "week": "2",
            "dayweather": "多云",
            "nightweather": "阴",
            "daytemp": "18",
            "nighttemp": "8",
            "daywind": "南",
            "nightwind": "南",
            "daypower": "1-3",
            "nightpower": "1-3",
            "daytemp_float": "18.0",
            "nighttemp_float": "8.0"
        }, {
            "date": "2025-12-17",
            "week": "3",
            "dayweather": "阴",
            "nightweather": "多云",
            "daytemp": "14",
            "nighttemp": "6",
            "daywind": "北",
            "nightwind": "北",
            "daypower": "1-3",
            "nightpower": "1-3",
            "daytemp_float": "14.0",
            "nighttemp_float": "6.0"
        }, {
            "date": "2025-12-18",
            "week": "4",
            "dayweather": "晴",
            "nightweather": "晴",
            "daytemp": "14",
            "nighttemp": "10",
            "daywind": "东",
            "nightwind": "东",
            "daypower": "1-3",
            "nightpower": "1-3",
            "daytemp_float": "14.0",
            "nighttemp_float": "10.0"
        }]
        """

        if msg_type != "ToolMessage":
            continue
        content = json.loads(content[0].get('text'))

        for single_content in content["forecasts"]:
            if single_content.get("week", "") and single_content["date"] in dates:
                weathers.append(build_weather(single_content))
    return weathers


def build_hotel(content, central_attraction_name, accommodation):
    hotel_price_config = {"经济型": {"price_range": "200以内", "estimated_cost": 160},
                          "舒适型": {"price_range": "200-400", "estimated_cost": 300},
                          "豪华型": {"price_range": "400-1000", "estimated_cost": 600}}

    lon_str, lat_str = content["location"].split(",")
    return Hotel(
        name=content["name"],
        address=content["address"],
        location=Location(longitude=float(lon_str), latitude=float(lat_str)),
        rating=content.get("rating", "暂无评分"),
        type=content["type"],
        description=content.get("description", f"距离{central_attraction_name}景点 1 公里内"),
        price_range=hotel_price_config[accommodation]["price_range"],
        estimated_cost=hotel_price_config[accommodation]["estimated_cost"],
    )


def parse_hotel_data(messages, central_attraction_name, accommodation):
    hotels = []

    print("=== //消息解析结果// ===")
    for idx, msg in enumerate(messages, 1):
        # 获取消息类型
        msg_type = msg.__class__.__name__
        # 提取消息内容
        content = getattr(msg, 'content', '')

        """
            {
                "id": "B000ABBX3R",
                "name": "如家酒店(北京潘家园店)",
                "location": "116.452186,39.871213",
                "address": "华威南路弘善家园304号",
                "business_area": "",
                "city": "北京市",
                "type": "住宿服务;宾馆酒店;经济型连锁酒店",
                "alias": "北京丽晶四季酒店",
                "photo": "https://store.is.autonavi.com/showpic/b64abab4695e8d7721f67c4886b91ff6",
                "cost": "",
                "star": "",
                "opentime2": "",
                "rating": "4.6",
                "lowest_price": "",
                "hotel_ordering": "1",
                "open_time": ""
            }
        """

        if msg_type != "ToolMessage":
            continue
        content = json.loads(content[0].get('text'))
        if content.get("location", ""):
            hotels.append(build_hotel(content, central_attraction_name, accommodation))
    return hotels

def build_meal(content):
    print(f"美食信息：{content}")
    lon_str, lat_str = content["location"].split(",")
    return Meal(
        name=content["name"],
        address=content["address"],
        location=Location(longitude=float(lon_str), latitude=float(lat_str)),
        type=content["type"],
        rating=content["rating"],
    )


def parse_meal_data(messages):
    meals = []

    print("=== //消息解析结果// ===")
    for idx, msg in enumerate(messages, 1):
        # 获取消息类型
        msg_type = msg.__class__.__name__
        # 提取消息内容
        content = getattr(msg, 'content', '')

        """
            {
                "id": "B0FFFTCGNX",
                "name": "景运门故宫餐厅",
                "location": "116.398455,39.918509",
                "address": "故宫博物院内(保和殿东侧景运门外、钟表馆对面)",
                "business_area": "",
                "city": "北京市",
                "type": "餐饮服务;中餐厅;中餐厅",
                "alias": "",
                "photo": "https://aos-comment.amap.com/B0FFFTCGNX/comment/D7E9CF11_EC09_419A_9D9C_8674D4CC28B7_L0_001_2000_170_1765257909768_77732275.jpg",
                "cost": "56.00",
                "opentime2": "周二至周日 08:30-15:30",
                "rating": "3.9",
                "open_time": "",
                "meal_ordering": "0"
            }
        """

        # 只处理 ToolMessage 类型
        if msg_type != "ToolMessage":
            continue
        content = json.loads(content[0].get('text'))

        if content.get("meal_ordering", ""):
            meals.append(build_meal(content))
    return meals


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


if __name__ == '__main__':
    print(build_attraction({
            "id": "B000A7O1CU",
            "name": "颐和园",
            "location": "116.275179,39.999617",
            "address": "新建宫门路19号",
            "business_area": "",
            "city": "北京市",
            "type": "风景名胜;风景名胜;世界遗产",
            "alias": "",
            "photo": "http://store.is.autonavi.com/showpic/a4b326f43a84d36b581d7f6e856fe858",
            "cost": "",
            "opentime2": "旺季:4月1日至10月31日:06:00-20:00(19:00停止进入)；淡季:11月1日至3月31日:06:30-19:00(18:00停止进入)",
            "level": "AAAAA",
            "rating": "4.9",
            "open_time": "",
            "ticket_ordering": "0"
    }))


