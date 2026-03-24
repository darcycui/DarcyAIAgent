import asyncio
import importlib
import importlib.util
import re
from pathlib import Path
from typing import Any, Optional


class SkillManager:
    """
    技能管理器
    """

    def __init__(self, skills_dir: str = None):
        if skills_dir is None:
            # 默认使用 config/skills 目录
            self.skills_dir = Path(__file__).parent.parent.parent / "config" / "skills"
        else:
            self.skills_dir = Path(skills_dir)
        # 已加载的 skills 元数据
        self.skills_metadata: dict[str, dict[str, Any]] = {}
        # 已加载的 skill 模块缓存
        self._module_cache: dict[str, dict[str, Any]] = {}

    def parse_skill_metadata(self, manifest_path: Path) -> dict[str, Any]:
        """
        解析技能元数据
        """
        if not manifest_path.exists():
            return {}
        content = manifest_path.read_text(encoding="utf-8")
        yaml_match = re.search(r"---\s*\n(.*?)\n---", content, re.DOTALL)
        if not yaml_match:
            return {}
        yaml_content = yaml_match.group(1)
        metadata = {}
        # 提取 name description 元数据
        for line in yaml_content.split("\n"):
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
        return metadata

    def load_skill_scripts(self, skill_id: str, scripts_dir:Path) -> dict[str, Any]:
        """
        加载技能的 Python 脚本
        """
        if not scripts_dir.exists():
            return {}
        functions = {}

        for py_file in sorted(scripts_dir.glob("*.py")):
            module = self._load_python_module(skill_id, py_file)
            if module:
                # 提取模块中的所有可调用函数（排除私有函数）
                for attr_name in dir(module):
                    if not attr_name.startswith('_') and callable(getattr(module, attr_name)):
                        func = getattr(module, attr_name)
                        functions[attr_name] = {
                            'function': func,
                            'source_file': str(py_file),
                        }

        return functions

    def _load_python_module(self, skill_id: str, script_path: Path):
        """
        动态加载 Python 脚本模块
        """
        if not script_path.exists():
            return None

        try:
            # 使用 importlib 动态加载模块
            spec = importlib.util.spec_from_file_location(
                f"skill_{skill_id}_{script_path.stem}",
                script_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            return module
        except Exception as e:
            print(f"[Skill] Error loading {script_path}: {e}")
            return None

    def discover_skills(self):
        """
        发现所有 skills 并加载元数据（不加载具体脚本）
        """
        if not self.skills_dir.exists():
            print(f"[Skill] Skills directory not found: {self.skills_dir}")
            return

        # 遍历所有 skill 目录
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_id = skill_dir.name
            print(f"[Skill] Discovering skill: {skill_id}")

            # 1. 解析 SKILL.md
            manifest_path = skill_dir / "SKILL.md"
            metadata = self.parse_skill_metadata(manifest_path)

            if not metadata:
                print(f"[Skill] Warning: No valid manifest found for {skill_id}")
                continue

            skill_name = metadata.get('name', skill_id)
            skill_description = metadata.get('description', '')

            # 2. 检查 scripts 目录是否存在
            scripts_dir = skill_dir / "scripts"
            has_scripts = scripts_dir.exists() and any(scripts_dir.glob("*.py"))

            if not has_scripts:
                print(f"[Skill] Warning: No scripts found for {skill_id}")
                continue

            # 3. 注册 skill 元数据（不加载具体脚本）
            self.skills_metadata[skill_name] = {
                'id': skill_id,
                'name': skill_name,
                'description': skill_description,
                'path': str(skill_dir),
                'scripts_dir': str(scripts_dir),
                'instructions': metadata.get('instructions', []),
                'examples': metadata.get('examples', []),
                'is_loaded': False,  # 标记脚本尚未加载
            }

            print(f"[Skill] Loaded metadata for: {skill_name}")

    def load_skill_on_demand(self, skill_name: str) -> bool:
        """
        按需加载 skill 的脚本（懒加载）
        """
        if skill_name not in self.skills_metadata:
            print(f"[Skill] Skill not found: {skill_name}")
            return False

        skill_info = self.skills_metadata[skill_name]

        # 如果已经加载过，直接返回
        if skill_info['is_loaded']:
            return True

        # 加载脚本
        scripts_dir = Path(skill_info['scripts_dir'])
        functions = self.load_skill_scripts(skill_info['id'], scripts_dir)

        if not functions:
            print(f"[Skill] Warning: No functions loaded for {skill_name}")
            return False

        # 缓存加载结果
        self._module_cache[skill_name] = functions
        skill_info['is_loaded'] = True

        print(f"[Skill] Loaded {len(functions)} function(s) for: {skill_name}")
        return True

    def get_all_skill_schemas(self) -> list[dict[str, Any]]:
        """
        获取所有 skill 的 schema（用于传递给 LLM）
        包含完整的技能描述和使用指南
        """
        schemas = []

        for skill_name, skill_info in self.skills_metadata.items():
            # 构建详细的 description，包含使用指南
            description_parts = [
                skill_info['description'],
            ]

            # 添加使用指南
            if skill_info['instructions']:
                description_parts.append("\nUsage Guidelines:")
                for instruction in skill_info['instructions']:
                    description_parts.append(f"- {instruction}")

            # 添加示例
            if skill_info['examples']:
                description_parts.append("\nExamples:")
                for example in skill_info['examples']:
                    description_parts.append(f"Input: \"{example['input']}\" → Output: \"{example['output']}\"")

            full_description = "\n".join(description_parts)

            # 为每个技能的主要函数生成 schema
            # 这里假设每个 skill 有一个主函数（或者可以根据实际情况调整）
            schema = {
                "type": "function",
                "function": {
                    "name": f"use_skill_{skill_name}",
                    "description": full_description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text content to process with this skill.",
                            },
                            "step": {
                                "type": "string",
                                "description": "Optional: specific step or function name to execute (if the skill has multiple steps).",
                                "default": "main"
                            }
                        },
                        "required": ["text"],
                    },
                },
            }
            schemas.append(schema)

        return schemas

    def execute_skill(self, skill_name: str, text: str, step: str = None) -> str:
        """
        执行 skill（懒加载 + 按需调用）

        Args:
            skill_name: skill 名称
            text: 要处理的文本
            step: 可选，指定执行的步骤/函数名

        Returns:
            执行结果
        """
        # 1. 按需加载 skill
        if not self.load_skill_on_demand(skill_name):
            return f"[Error] Failed to load skill: {skill_name}"

        # 2. 获取已加载的函数
        functions = self._module_cache.get(skill_name, {})

        if not functions:
            return f"[Error] No functions available for skill: {skill_name}"

        # 3. 确定要调用的函数
        if step and step in functions:
            # 调用指定的步骤
            func_info = functions[step]
        elif 'format_text' in functions:
            # 默认调用 format_text（如果存在）
            func_info = functions['format_text']
        elif len(functions) == 1:
            # 只有一个函数时调用它
            func_info = list(functions.values())[0]
        else:
            # 尝试找主函数
            main_candidates = ['main', 'process', 'execute', 'run']
            func_info = None
            for candidate in main_candidates:
                if candidate in functions:
                    func_info = functions[candidate]
                    break

            if not func_info:
                return f"[Error] No suitable function found for skill: {skill_name}. Available: {list(functions.keys())}"

        # 4. 执行函数
        try:
            func = func_info['function']

            # 检查是否是异步函数
            if asyncio.iscoroutinefunction(func):
                result = asyncio.run(func(text))
            else:
                result = func(text)

            return str(result)
        except Exception as e:
            return f"[Error] Execution failed: {e}"

    def get_skill_metadata(self, skill_name: str) -> Optional[dict[str, Any]]:
        """
        获取 skill 的元数据（不加载脚本）
        """
        return self.skills_metadata.get(skill_name)

    def list_all_skills(self) -> list[dict[str, Any]]:
        """
        列出所有可用的 skill（仅元数据）
        """
        return list(self.skills_metadata.values())

# 全局单例
_skill_manager_instance = None

def get_skill_manager() -> SkillManager:
    """获取全局 Skill Manager 实例"""
    global _skill_manager_instance
    if _skill_manager_instance is None:
        _skill_manager_instance = SkillManager()
        _skill_manager_instance.discover_skills()
    return _skill_manager_instance