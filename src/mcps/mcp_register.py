import asyncio
import traceback
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from mcps.callback_wrap import create_dynamic_tool_caller
from mcps.mcp_global_helper import get_mcp_manager
from tools.tools_register import TOOLS


def get_mcp_tools_wrapper():
    """
    获取 MCP 工具的包装器
    将 MCP 工具动态添加到 TOOLS 字典中
    """
    mcp_manager = get_mcp_manager()
    if not mcp_manager:
        return {}

    mcp_tools_schemas = mcp_manager.get_all_tools_schemas()
    mcp_tools = {}

    for schema in mcp_tools_schemas:
        tool_name = schema["function"]["name"]
        # 创建动态调用函数
        dynamic_function = create_dynamic_tool_caller(tool_name)
        mcp_tools[tool_name] = {
            "function": dynamic_function,
            "schema": schema,
        }
    # print(f"[MCP] Registered MCP tool: {mcp_tools}")
    return mcp_tools

