"""
GogoClaw 智能体模块 - 工具定义
"""
from typing import Dict, Any, List, Callable, Optional
import json
import logging

logger = logging.getLogger(__name__)


# 内置工具定义 (JSON Schema 格式，用于 LLM 函数调用)
BUILTIN_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a shell command in the sandbox. Use this for running programs, scripts, system operations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 30)",
                        "default": 30
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file from the filesystem.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Line offset to start reading from",
                        "default": 0
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of lines to read",
                        "default": 100
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file. Creates the file if it doesn't exist, overwrites if it does.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and directories in a given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to list"
                    },
                    "include_hidden": {
                        "type": "boolean",
                        "description": "Include hidden files",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Search for files matching a pattern or content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Search pattern (glob or content)"
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory to search in",
                        "default": "."
                    },
                    "content_search": {
                        "type": "boolean",
                        "description": "Search file contents (not just names)",
                        "default": False
                    }
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_navigate",
            "description": "Navigate a browser to a URL and interact with the page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to navigate to"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["goto", "click", "type", "screenshot", "get_html", "scroll"],
                        "description": "Browser action to perform"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for element to interact with"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to type (for 'type' action)"
                    }
                },
                "required": ["url", "action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "manage_session",
            "description": "Manage conversation sessions - list, send to, or spawn new sessions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "send", "spawn", "history"],
                        "description": "Session action"
                    },
                    "target_session_id": {
                        "type": "string",
                        "description": "Target session ID (for send/spawn/history actions)"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message to send (for send action)"
                    }
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_memory",
            "description": "Search through conversation history and long-term memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    }
]


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._definitions: List[Dict[str, Any]] = []
        
    def register(self, name: str, func: Callable, definition: Dict[str, Any]):
        """注册工具"""
        self._tools[name] = func
        self._definitions.append(definition)
        
    def get_tool(self, name: str) -> Optional[Callable]:
        """获取工具函数"""
        return self._tools.get(name)
        
    def get_definitions(self) -> List[Dict[str, Any]]:
        """获取所有工具定义"""
        return self._definitions
        
    def get_definition(self, name: str) -> Optional[Dict[str, Any]]:
        """获取单个工具定义"""
        for d in self._definitions:
            if d.get("function", {}).get("name") == name:
                return d
        return None


# 全局工具注册表
_tool_registry = ToolRegistry()


def get_builtin_tools() -> List[Dict[str, Any]]:
    """获取内置工具定义"""
    return BUILTIN_TOOLS.copy()


def get_tool_registry() -> ToolRegistry:
    """获取工具注册表"""
    return _tool_registry


def register_tool(name: str, func: Callable, definition: Dict[str, Any]):
    """注册自定义工具"""
    _tool_registry.register(name, func, definition)
