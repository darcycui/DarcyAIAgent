# ============================================================
# Agent Loop — 核心
# 基础流程： LLM call → parse tool_calls → execute → append results to messages → loop or exit
# 安全设置：为while循环设置了一个迭代的安全上限：20 轮（MAX_TURNS=200）
# 使用全局变量message作为上下文的载体，累积系统提示词、用户消息、助手响应和工具结果
#
# 其中，变量message按如下规则更新
# 使用System Prompt初始化：{"role": "system", "content": system_prompt}
# 追增User Message：{"role": "user", "content": user_message}
# 追加Tool Results：{"role": "tool", "content": result}
#
# 注：这里使用的模型为deepseek-chat，主要考量因素是模型支持Tool Calls，并且完全兼容OpenAI的SDK。
# ============================================================
import json

from openai import OpenAI

from tools.tools_register import TOOLS

MAX_TURNS = 20


def agent_loop(user_message: str, messages: list, client: OpenAI) -> str:
    """
    Agent Loop：while 循环驱动 LLM 推理与工具调用。
    流程：
      1. 将用户消息追加到 messages
      2. 调用 LLM
      3. 若 LLM 返回 tool_calls → 逐个执行 → 结果追加到 messages → 继续循环
      4. 若 LLM 直接返回文本（无 tool_calls）→ 退出循环，返回文本
      5. 安全上限 MAX_TURNS 轮
    """
    messages.append({"role": "user", "content": user_message})
    tool_schemas = [t["schema"] for t in TOOLS.values()]
    for turn in range(1, MAX_TURNS + 1):
        # --- LLM Call ---
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tool_schemas,
        )
        choice = response.choices[0]
        assistant_msg = choice.message
        # 将 assistant 消息追加到上下文
        messages.append(assistant_msg.model_dump())
        # --- 终止条件：无 tool_calls ---
        if not assistant_msg.tool_calls:
            return assistant_msg.content or ""
        # --- 执行每个 tool_call ---
        for tool_call in assistant_msg.tool_calls:
            name = tool_call.function.name
            raw_args = tool_call.function.arguments
            print(f"  [tool] {name}({raw_args})")
            # 解析参数并调用工具
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}
            tool_entry = TOOLS.get(name)
            if tool_entry is None:
                result = f"[error] unknown tool: {name}"
            else:
                result = tool_entry["function"](**args)
            # 将工具结果追加到上下文
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )
    return "[agent] reached maximum turns, stopping."
