import unittest

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from mcps.mcp_register import create_dynamic_tool_caller


class TestCallbackWrap(unittest.IsolatedAsyncioTestCase):
    """测试 callback_wrap.py 中的动态工具调用功能"""

    def setUp(self):
        """测试前的准备工作"""
        pass

    def tearDown(self):
        """测试后的清理工作"""
        pass

    async def test_create_dynamic_tool_caller_returns_async_function(self):
        """测试 create_dynamic_tool_caller 返回的是异步函数"""
        tool_name = "test__tool"
        dynamic_function = create_dynamic_tool_caller(tool_name)

        # 验证返回的是可等待的异步函数
        self.assertTrue(asyncio.iscoroutinefunction(dynamic_function))

    async def test_dynamic_tool_caller_with_mock_manager(self):
        """测试动态工具调用器（使用 mock 的 MCP 管理器）"""
        tool_name = "test__example_tool"
        mock_args = {"param1": "value1", "param2": "value2"}
        expected_result = "mocked response"

        # 创建 mock 的 MCP manager
        mock_manager = AsyncMock()
        mock_call_method = AsyncMock(return_value=expected_result)
        mock_manager.call_mcp_tool = mock_call_method

        # Patch get_mcp_manager 返回 mock 对象
        with patch('mcps.callback_wrap.get_mcp_manager', return_value=mock_manager):
            # 创建动态工具调用器
            dynamic_function = create_dynamic_tool_caller(tool_name)
            # 调用工具
            result = await dynamic_function(**mock_args)
            # 验证结果
            self.assertEqual(expected_result, result)
            # 验证 call_mcp_tool 被正确调用
            mock_manager.call_mcp_tool.assert_called_once_with(
                tool_name,
                mock_args
            )

if __name__ == '__main__':
    unittest.main()
