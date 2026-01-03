import asyncio
import os
from typing import List, Any

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

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


llm = init_chat_model(
    model=os.getenv("LLM_MODEL_ID"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    temperature=0,
    max_tokens=8000
)

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
        print(f"内容: {content if content else '<空>'}", type(content))
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


async def run_agent():
    tools = await get_tools()
    agent = create_agent(
        model=llm,
        system_prompt="你是一个AI助手，使用高德地图工具获取信息",
        tools=tools
    )

    # response = await agent.ainvoke({"messages": [{"role": "user", "content": "帮我查一下北京的景点"}]})
    # response = await agent.ainvoke({"messages": [{"role": "user", "content": "请搜索北京的故宫博物院周围1公里的经济型酒店，然后挑选已经搜索出来的1个酒店的详情信息"}]})
    # response = await agent.ainvoke({"messages": [{"role": "user", "content": "帮我查一下杭州天气"}]})
    response = await agent.ainvoke({"messages": [{"role": "user", "content": "帮我搜索开封的特色美食，并按照早中晚三餐进行安排1天的餐饮情况，提供给我最终美食地点的详细信息"}]})

    parse_messages(response["messages"])

if __name__ == "__main__":
    asyncio.run(run_agent())
