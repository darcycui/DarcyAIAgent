import asyncio
import unittest

from mcps.mcp_global_helper import init_mcp, shutdown_mcp, get_mcp_manager
from mcps.mcp_register import get_mcp_tools_wrapper


class MyTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    async def test_weather_mcp_connect(self):
        print("\n[MCP] Initializing MCP servers...")
        result = await init_mcp()
        self.assertEqual(True, result, "初始化 MCP 失败")
        print("[MCP] Initialization complete.\n")
        get_mcp_tools_wrapper()
        weather_forecast = await get_mcp_manager().call_mcp_tool("weather__get_forecast", {"city": "上海"})
        print(f"[MCP] weather_forecast: {weather_forecast}")
        await shutdown_mcp()


if __name__ == '__main__':
    unittest.main()
