import asyncio
import traceback

from main import init_client, init_messages, run_darcy_agent
from skills.skill_manager import init_skill
from mcps.mcp_manager import init_mcp, shutdown_mcp
from uis.views.components import setup_ui, setup_ui_vertical
from utils.api_key_util import get_api_key_deepseek

api_key = get_api_key_deepseek()
client = init_client(api_key)
messages = init_messages()

def greet(name: str) -> str:
    print(f"输入文本: {name}")
    # 调用 run_darcy_agent
    # 使用 asyncio.run() 调用异步函数
    async def process_request():
        # 初始化 Skill 系统（仅加载元数据）
        init_skill()
        # 初始化 MCP
        await init_mcp()
        reply = await run_darcy_agent(name, client, messages)
        return reply

    # 执行异步调用
    result = asyncio.run(process_request())
    return result if result else f"回答错误"


# demo = setup_ui(greet)
demo = setup_ui_vertical(greet)

# 执行结果
# share=False 本地运行
# Running on local URL:  http://127.0.0.1:7860
# share=True 本地运行 并生成公网访问地址（一周有效）
# Running on local URL:  http://127.0.0.1:7860
# Running on public URL: https://98432096958f809514.gradio.live
if __name__ == "__main__":
    # 本地运行
    # demo.launch(share=False)

    # 本地运行 并生成公网访问地址（一周有效）
    # demo.launch(share=True)

    # 本地运行 并生成局域网访问地址 http://127.0.0.1:7860(本机) http://本机IP:7860(局域网其他设备)
    try:
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )
    except Exception as e:
        print(f"运行异常: {e}")
        traceback.print_exc()

    finally:
        # 清理 MCP 连接
        print("\n[MCP] Shutting down MCP servers...")
        asyncio.run(shutdown_mcp())
        print("[MCP] Shutdown complete.")
