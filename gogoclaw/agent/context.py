"""
GogoClaw 智能体模块 - 上下文组装
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Context:
    """上下文"""
    system_prompt: str
    chat_history: List[Dict[str, str]]
    tools: List[Dict[str, Any]]
    memory_context: Optional[str] = None
    skills_context: Optional[List[str]] = None


class SystemPromptBuilder:
    """系统提示词构建器"""
    
    # 默认基础提示词
    BASE_PROMPT = """You are GogoClaw, an AI assistant that helps users with various tasks.

## Core Principles
- Be helpful, concise, and accurate
- Think step by step when solving problems
- Ask for clarification when needed
- Admit when you don't know something

## Capabilities
- You can execute commands in a sandboxed environment
- You can browse the web and read files
- You have access to various tools to help accomplish tasks

## Safety Guidelines
- Do not execute harmful commands
- Do not reveal sensitive information
- Always prioritize user safety
"""
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        
        # 配置文件路径
        self.agents_md = workspace_dir / "AGENTS.md"
        self.soul_md = workspace_dir / "SOUL.md"
        self.tools_md = workspace_dir / "TOOLS.md"
        self.memory_md = workspace_dir / "MEMORY.md"
        
    def build(
        self,
        agent_config: Dict[str, Any],
        session_history: List[Dict[str, str]],
        relevant_memories: Optional[List[str]] = None,
        session_trust_level: str = "dm"
    ) -> Context:
        """构建完整上下文"""
        
        # 1. 构建系统提示词
        system_prompt = self._build_system_prompt(
            agent_config,
            relevant_memories,
            session_trust_level
        )
        
        # 2. 构建聊天历史
        chat_history = self._build_chat_history(session_history)
        
        # 3. 获取工具定义
        tools = self._get_tools(agent_config.get("tools", []))
        
        return Context(
            system_prompt=system_prompt,
            chat_history=chat_history,
            tools=tools,
            memory_context="\n\n".join(relevant_memories) if relevant_memories else None
        )
        
    def _build_system_prompt(
        self,
        agent_config: Dict[str, Any],
        relevant_memories: Optional[List[str]],
        trust_level: str
    ) -> str:
        """构建系统提示词"""
        parts = [self.BASE_PROMPT]
        
        # 添加 AGENTS.md (核心指令)
        if self.agents_md.exists():
            try:
                content = self.agents_md.read_text(encoding="utf-8")
                parts.append(f"\n\n## Agent Rules\n{content}")
            except Exception as e:
                logger.warning(f"Error reading AGENTS.md: {e}")
                
        # 添加 SOUL.md (人格)
        if self.soul_md.exists():
            try:
                content = self.soul_md.read_text(encoding="utf-8")
                parts.append(f"\n\n## Personality\n{content}")
            except Exception as e:
                logger.warning(f"Error reading SOUL.md: {e}")
                
        # 添加 TOOLS.md (工具备注)
        if self.tools_md.exists():
            try:
                content = self.tools_md.read_text(encoding="utf-8")
                parts.append(f"\n\n## Tool Notes\n{content}")
            except Exception as e:
                logger.warning(f"Error reading TOOL: {e}")
                
        # 添加记忆 (仅在主会话/DM)
        if relevant_memories and trust_level in ["main", "dm"]:
            memories_text = "\n\n".join(relevant_memories)
            parts.append(f"\n\n## Relevant Memories\n{memories_text}")
            
        # 添加用户配置的系统提示词
        custom_prompt = agent_config.get("system_prompt")
        if custom_prompt:
            parts.append(f"\n\n{custom_prompt}")
            
        # 添加信任级别相关的指令
        if trust_level == "group":
            parts.append("\n\n## Group Chat Guidelines\n- Only respond when mentioned or directly asked\n- Be mindful that this is a group setting")
        elif trust_level == "dm":
            parts.append("\n\n## DM Guidelines\n- This is a private conversation\n- Standard helpfulness applies")
            
        return "\n\n".join(parts)
        
    def _build_chat_history(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """构建聊天历史"""
        # 限制历史长度
        max_messages = 20
        return history[-max_messages:] if len(history) > max_messages else history
        
    def _get_tools(self, tool_names: List[str]) -> List[Dict[str, Any]]:
        """获取工具定义"""
        # 这里应该从工具注册表获取
        # 简化版本返回内置工具定义
        from gogoclaw.agent.tools import get_builtin_tools
        
        all_tools = get_builtin_tools()
        
        # 筛选需要的工具
        if not tool_names or "all" in tool_names:
            return all_tools
            
        return [t for t in all_tools if t["function"]["name"] in tool_names]


class SkillsManager:
    """技能管理器"""
    
    def __init__(self, workspace_dir: Path):
        self.skills_dir = workspace_dir / "skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        
    def get_relevant_skills(self, query: str, max_skills: int = 3) -> List[str]:
        """获取相关的技能文件"""
        # 简单实现: 基于文件名匹配
        # 实际应该用向量搜索
        skills = []
        
        if not self.skills_dir.exists():
            return skills
            
        for skill_file in self.skills_dir.glob("*.md"):
            # 简单检查: 文件名是否在查询中
            skill_name = skill_file.stem.lower()
            if skill_name in query.lower():
                try:
                    content = skill_file.read_text(encoding="utf-8")
                    skills.append(content)
                    if len(skills) >= max_skills:
                        break
                except Exception as e:
                    logger.warning(f"Error reading skill {skill_file}: {e}")
                    
        return skills
