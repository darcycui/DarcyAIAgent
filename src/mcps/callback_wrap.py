from mcps.mcp_global_helper import get_mcp_manager


def create_dynamic_tool_caller(qualified_name: str):
    """创建一个用于调用特定MCP工具的闭包函数"""

    async def dynamic_tool_function(**kwargs):
        # 这个函数将被Agent Loop调用
        # 通过您实现的MCP通信层发送请求
        response = await get_mcp_manager().call_mcp_tool(qualified_name, kwargs)
        return response

    return dynamic_tool_function
