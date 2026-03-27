import unittest

from main import init_client_zhipu_glm, init_messages
from tools.tools_register import TOOLS
from utils.api_key_util import get_api_key_zhipu_glm

# 测试 glm-4.7v-flash 大模型 api (免费 但是有速率限制)
class TestZhiPuApiCall(unittest.TestCase):
    def test_zhipu_api_call(self):
        # --- LLM Call ---
        api_key = get_api_key_zhipu_glm()
        client = init_client_zhipu_glm(api_key)
        messages: list = init_messages()
        messages.append({"role": "user", "content": "你是哪个大模型？"})
        # 可以本地调用的工具 (函数)
        all_tools = TOOLS.copy()
        # 给大模型传递的工具 schema
        tool_schemas = [t["schema"] for t in all_tools.values()]
        response = client.chat.completions.create(
            model="glm-4.7-flash",
            messages=messages,
            tools=tool_schemas,
        )
        choice = response.choices[0]
        assistant_msg = choice.message
        print(f"-->{assistant_msg}")


if __name__ == '__main__':
    unittest.main()
