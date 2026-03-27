# 用户交互界面设计 - Python CLI REPL
import asyncio

from openai import OpenAI

from core.llm_loop import agent_loop
from prompt.system_prompt import SYSTEM_PROMPT
from mcps.mcp_manager import init_mcp, shutdown_mcp
from skills.skill_manager import init_skill
from utils.api_key_util import get_api_key_deepseek


async def main():
    api_key = get_api_key_deepseek()
    client = init_client(api_key)
    messages: list = init_messages()
    # 初始化 Skill 系统（仅加载元数据）
    init_skill()
    # 初始化 MCP
    await init_mcp()
    print("Agent ready. Type your message (or 'exit' to quit, 'clear' to reset).\n")
    try:
        while True:
            try:
                user_input = input("You> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye.")
                break
            await run_darcy_agent(user_input, client, messages)
    finally:
        # 清理 MCP 连接
        print("\n[MCP] Shutting down MCP servers...")
        asyncio.run(shutdown_mcp())
        print("[MCP] Shutdown complete.")


def init_messages() -> list[dict[str, str]]:
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def init_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


async def run_darcy_agent(_user_input: str, _client, _messages) -> str:
    if not _user_input:
        print("输入内容为空 请重新输入")
    if _user_input.lower() == "exit":
        print("Bye.")
    if _user_input.lower() == "clear":
        _messages.clear()
        _messages.append({"role": "system", "content": SYSTEM_PROMPT})
        print("(context cleared)\n")
    reply = await agent_loop(_user_input, _messages, _client)
    print(f"\nAgent> {reply}\n")
    return reply


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    asyncio.run(main())
