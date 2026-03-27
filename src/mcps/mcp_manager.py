import json
from pathlib import Path
from typing import Any, Optional

from mcps.mcp_client import MCPClient


class MCPManager:
    """
    MCP 管理器，管理多个 MCP Server 连接
    """

    def __init__(self, config_path: str = None):
        if config_path is None:
            # 使用当前文件为基准，计算项目根目录
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.config_path = str(base_dir / "config" / "mcp_config.json")
        else:
            self.config_path = config_path
        self.clients: dict[str, MCPClient] = {}
        self.config: dict = {}

    def load_config(self) -> bool:
        """
        加载配置文件
        :return: 是否成功
        """
        try:
            print(f"正在加载配置文件 {self.config_path}")
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 从嵌套结构中提取 mcpServers
            if "mcpServers" in data:
                self.config = data["mcpServers"]
            else:
                raise ValueError("Invalid config file: no mcpServers field")
            print(f"解析-->{self.config}")
            return True if self.config else False
        except Exception as e:
            print(f"加载配置文件 error: {e}")
            return False

    async def connect_all(self):
        """
        连接所有 MCP Server
        """
        for server_name, config in self.config.items():
            if config.get("disabled", True):
                continue
            client = MCPClient(server_name, config)
            await client.connect()
            self.clients[server_name] = client
            print(f"已连接 MCP Server {server_name}")

    def get_all_tools_schemas(self) -> list[dict]:
        """
        获取所有 MCP Server 的工具列表
        :return: 工具列表（OpenAI Function Calling 格式）
        """
        all_schemas = []
        for client in self.clients.values():
            schemas = client.get_tools_schemas()
            for schema in schemas:
                mcp_tool_name = schema.get("name", "")
                if not mcp_tool_name:
                    continue
                openai_schema = {
                    "type": "function",
                    "function": {
                        "name": f"{client.server_name}__{mcp_tool_name}",
                        "description": schema.get("description", ""),
                        "parameters": schema.get("inputSchema", schema.get("parameters", {}))
                    }
                }
                all_schemas.append(openai_schema)
        return all_schemas

    async def call_mcp_tool(self, qualified_name: str, arguments: dict[str, Any]) -> str:
        """
        调用 MCP Server 的工具
        :param qualified_name: 工具名称 限定的工具名称（格式：server__tool_name）
        :param arguments: 工具参数
        :return: 工具执行结果
        """
        print(f"[MCP Manager] Calling tool: {qualified_name} with args: {arguments}")
        parts = qualified_name.split("__", 1)
        if len(parts) != 2:
            return f"输入的 MCPServer 名称格式错误: {qualified_name}"
        server_name, tool_name = parts
        client = self.clients.get(server_name)
        if not client:
            return f"MCP Server {server_name} not found"
        print(f"[MCP Manager] Found client for {server_name}, calling {tool_name}")
        return await client.call_tool(tool_name, arguments)

    async def disconnect_all(self):
        """
        断开所有 MCP Server 的连接
        """
        for client in self.clients.values():
            await client.disconnect()


def get_mcp_manager() -> Optional[MCPManager]:
    """获取全局 MCP 管理器实例"""
    return _mcp_manager


async def init_mcp() -> bool:
    """
    初始化 MCP
    Args:
        config_path: MCP 配置文件路径
    Returns:
        是否初始化成功
    """
    print("\n[MCP] Initializing MCP servers...")
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPManager()
        if not _mcp_manager.load_config():
            return False
        await _mcp_manager.connect_all()
    print("[MCP] Initialization complete.\n")
    return True


async def shutdown_mcp():
    """关闭 MCP 连接"""
    global _mcp_manager
    if _mcp_manager:
        await _mcp_manager.disconnect_all()
        _mcp_manager = None


_mcp_manager: Optional[MCPManager] = None
