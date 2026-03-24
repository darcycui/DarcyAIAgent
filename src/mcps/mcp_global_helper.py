from typing import Optional
from mcps.mcp_manager import MCPManager

# 全局 MCP 管理器实例
_mcp_manager: Optional[MCPManager] = None


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
    global _mcp_manager
    _mcp_manager = MCPManager()

    if not _mcp_manager.load_config():
        return False

    await _mcp_manager.connect_all()
    return True


async def shutdown_mcp():
    """关闭 MCP 连接"""
    global _mcp_manager
    if _mcp_manager:
        await _mcp_manager.disconnect_all()
        _mcp_manager = None
