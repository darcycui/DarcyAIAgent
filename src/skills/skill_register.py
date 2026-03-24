from skills.skill_manager import get_skill_manager


def create_skill_tool_wrapper(skill_name: str):
    """
    创建 skill 工具的包装器（支持懒加载和按需执行）
    """

    async def skill_executor(text: str, step: str = None) -> str:
        """
        动态执行 skill 的异步包装器
        """
        skill_manager = get_skill_manager()
        # 执行 skill（自动处理懒加载）
        result = skill_manager.execute_skill(skill_name, text, step)
        return result

    return skill_executor


def get_skill_tools_wrapper():
    """
    获取 Skill 工具的包装器
    将 Skill 工具动态添加到 TOOLS 字典中
    """
    skill_manager = get_skill_manager()
    if not skill_manager:
        return {}

    skill_tools = {}

    # 为每个 skill 创建一个工具入口
    for skill_name in skill_manager.skills_metadata.keys():
        tool_name = f"use_skill_{skill_name}"
        dynamic_function = create_skill_tool_wrapper(skill_name)

        skill_tools[tool_name] = {
            "function": dynamic_function,
            "schema": next(
                s for s in skill_manager.get_all_skill_schemas()
                if s["function"]["name"] == tool_name
            ),
        }

    print(f"[Skill] Registered {len(skill_tools)} skill tool(s)")
    return skill_tools
