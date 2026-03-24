# 用户交互界面设计 - Python CLI REPL
import os
import sys
import asyncio

from openai import OpenAI

from core.llm_loop import agent_loop
from prompt.system_prompt import SYSTEM_PROMPT
from mcps.mcp_global_helper import init_mcp, shutdown_mcp


async def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: please set DEEPSEEK_API_KEY environment variable.")
        sys.exit(1)
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    messages: list = [{"role": "system", "content": SYSTEM_PROMPT}]
    # 初始化 MCP
    print("\n[MCP] Initializing MCP servers...")
    await init_mcp()
    print("[MCP] Initialization complete.\n")
    print("Agent ready. Type your message (or 'exit' to quit, 'clear' to reset).\n")
    try:
        while True:
            try:
                user_input = input("You> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye.")
                break
            if not user_input:
                continue
            if user_input.lower() == "exit":
                print("Bye.")
                break
            if user_input.lower() == "clear":
                messages.clear()
                messages.append({"role": "system", "content": SYSTEM_PROMPT})
                print("(context cleared)\n")
                continue
            reply = await agent_loop(user_input, messages, client)
            print(f"\nAgent> {reply}\n")
    finally:
        # 清理 MCP 连接
        print("\n[MCP] Shutting down MCP servers...")
        asyncio.run(shutdown_mcp())
        print("[MCP] Shutdown complete.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    asyncio.run(main())
