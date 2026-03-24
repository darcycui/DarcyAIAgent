import asyncio
import json
import traceback
from typing import Optional, Any

from mcp import stdio_client, ClientSession, StdioServerParameters


class MCPClient:
    def __init__(self, server_name: str, config: dict[str, Any]):
        """
        初始化 MCP 客户端
        :param server_name: Server 名称
        :param config: Server 配置 (包含 command args env)
        """
        self.stdio_transport = None
        self.server_name = server_name
        self.config = config
        self.session: Optional[ClientSession] = None
        self.tools_cache: list[dict] = []
        self._stdio_transport = None
        self._read_stream = None
        self._write_stream = None
        self._loop = None  # 保存创建 session 时的事件循环

    async def connect(self):
        """连接到 MCP Server"""
        if self.config.get("disabled", True):
            print(f"[MCP Client] {self.server_name} is disabled")
            return
        # 保存当前事件循环
        self._loop = asyncio.get_running_loop()
        server_params = StdioServerParameters(
            command=self.config["command"],
            args=self.config.get("args", []),
        )
        try:
            self._stdio_transport = stdio_client(server_params)
            read_write = await self._stdio_transport.__aenter__()
            self._read_stream, self._write_stream = read_write
            self.session = ClientSession(self._read_stream, self._write_stream)
            await self.session.__aenter__()
            await self.session.initialize()

            tools_response = await self.session.list_tools()
            self.tools_cache = [tool.model_dump() for tool in tools_response.tools]
            print(f"[MCP Client] {self.server_name} connected, found {len(self.tools_cache)} tools: {self.tools_cache}")
        except Exception as e:
            print(f"[MCP Client] {self.server_name} connect error: {e}")
            print("完整异常堆栈:")
            traceback.print_exc()

    async def disconnect(self):
        """断开 MCP Server"""
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
            except Exception as e:
                print(f"关闭 session 时出错：{e}")
            finally:
                self.session = None

        if self._stdio_transport:
            try:
                await self._stdio_transport.__aexit__(None, None, None)
            except Exception as e:
                print(f"关闭 stdio_transport 时出错：{e}")
            finally:
                self._stdio_transport = None
                self._read_stream = None
                self._write_stream = None

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """
        调用 MCP Server 的工具
        :param tool_name: 工具名称
        :param arguments: 工具参数
        :return: 工具执行结果
        """
        try:
            print(f"[MCP Client] {self.server_name} call tool {tool_name} with args: {arguments}")
            if not self.session:
                raise Exception(f"[MCP Client] {self.server_name} not connected")
            # result = await self.session.call_tool(tool_name, arguments)
            # 添加超时控制
            result = await asyncio.wait_for(
                self.session.call_tool(tool_name, arguments),
                timeout=50
            )
            print(f"[MCP Client] Got result from {self.server_name}/{tool_name}")
            if result.content:
                content = result.content[0]
                if hasattr(content, 'text'):
                    print(f"[MCP Client] Result text: {content.text[:200]}...")
                    return content.text
                elif isinstance(content, dict):
                    return json.dumps(content)
                else:
                    return str(content)
            return f"[MCP Client] {self.server_name} call tool {tool_name} SUCCESS"
        except Exception as e:
            error_message = f"[MCP Client] {self.server_name} call tool {tool_name} error: {e}"
            print(f"{error_message}")
            return error_message

    def get_tools_schemas(self):
        """ 获取所有工具的 schemas"""
        return self.tools_cache
