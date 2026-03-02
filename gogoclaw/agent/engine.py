"""
GogoClaw 智能体模块 - Agent 引擎
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Callable, Awaitable
from pathlib import Path
from dataclasses import dataclass

from gogoclaw.gateway.protocol import Message, MessageRequest
from gogoclaw.agent.session import SessionManager, Session
from gogoclaw.agent.context import SystemPromptBuilder, Context
from gogoclaw.agent.tools import get_builtin_tools, ToolRegistry
from gogoclaw.agent.model_client import ModelClient, create_model_client, ModelResponse
from gogoclaw.memory.store import MemoryStore

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Agent 配置"""
    agent_id: str
    name: str
    model_provider: str
    model_name: str
    system_prompt: str
    tools: List[str]
    sandbox_enabled: bool
    memory_enabled: bool
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentConfig":
        model = data.get("model", {})
        return cls(
            agent_id=data.get("agent_id", "main"),
            name=data.get("name", "GogoClaw"),
            model_provider=model.get("provider", "openai"),
            model_name=model.get("model_name", "gpt-4o"),
            system_prompt=data.get("system_prompt", ""),
            tools=data.get("tools", ["command", "browser", "file"]),
            sandbox_enabled=data.get("sandbox_enabled", True),
            memory_enabled=data.get("memory_enabled", True)
        )


class ToolExecutor:
    """工具执行器"""
    
    def __init__(self, sandbox_enabled: bool = True):
        self.sandbox_enabled = sandbox_enabled
        self._tool_handlers: Dict[str, Callable] = {}
        
    def register_handler(self, tool_name: str, handler: Callable):
        """注册工具处理器"""
        self._tool_handlers[tool_name] = handler
        
    async def execute(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any],
        trust_level: str = "dm"
    ) -> str:
        """执行工具"""
        handler = self._tool_handlers.get(tool_name)
        
        if not handler:
            return json.dumps({
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self._tool_handlers.keys())
            })
            
        try:
            # 在沙箱中执行
            if self.sandbox_enabled and trust_level != "main":
                result = await self._execute_in_sandbox(handler, arguments)
            else:
                # 直接执行
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(**arguments)
                else:
                    result = handler(**arguments)
                    
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Tool execution error: {tool_name} - {e}", exc_info=True)
            return json.dumps({
                "error": str(e),
                "tool_name": tool_name,
                "arguments": arguments
            }, ensure_ascii=False)
            
    async def _execute_in_sandbox(
        self, 
        handler: Callable, 
        arguments: Dict[str, Any]
    ) -> Any:
        """在沙箱中执行"""
        # TODO: 实现 Docker 沙箱
        # 暂时直接执行
        if asyncio.iscoroutinefunction(handler):
            return await handler(**arguments)
        else:
            return handler(**arguments)


class AgentEngine:
    """Agent 引擎"""
    
    def __init__(
        self,
        agent_config: AgentConfig,
        storage_dir: Path,
        memory_store: Optional[MemoryStore] = None
    ):
        self.config = agent_config
        self.storage_dir = storage_dir
        self.memory_store = memory_store
        
        # 会话管理
        self.session_manager = SessionManager(storage_dir)
        
        # 上下文构建
        self.context_builder = SystemPromptBuilder(storage_dir / "workspace")
        
        # 工具执行
        self.tool_executor = ToolExecutor(sandbox_enabled=self.config.sandbox_enabled)
        
        # 模型客户端
        self._model_client = None
        
        # 注册内置工具
        self._register_builtin_tools()
        
    def _register_builtin_tools(self):
        """注册内置工具"""
        import subprocess
        import asyncio
        
        async def execute_command(command: str, timeout: int = 30, sandbox: bool = False) -> Dict:
            """
            执行命令
            
            Args:
                command: 要执行的命令
                timeout: 超时时间 (秒)
                sandbox: 是否在沙箱中执行 (暂未实现 Docker 沙箱)
            """
            try:
                # 安全检查：阻止危险命令
                dangerous_cmds = ["rm -rf", "sudo", "su ", "chmod 777", "dd if=", "> /dev/", "> /etc/"]
                for dangerous in dangerous_cmds:
                    if dangerous in command:
                        return {
                            "error": f"Dangerous command blocked: {dangerous}",
                            "exit_code": -1
                        }
                
                # 执行命令
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(self.storage_dir)
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=timeout
                    )
                    
                    return {
                        "output": stdout.decode("utf-8", errors="replace"),
                        "stderr": stderr.decode("utf-8", errors="replace"),
                        "exit_code": process.returncode or 0
                    }
                except asyncio.TimeoutError:
                    process.kill()
                    return {
                        "error": f"Command timeout after {timeout}s",
                        "exit_code": -1
                    }
                    
            except Exception as e:
                return {
                    "error": str(e),
                    "exit_code": -1
                }
            
        async def read_file(path: str, offset: int = 0, limit: int = 100) -> Dict:
            """读取文件"""
            try:
                p = Path(path)
                if not p.exists():
                    return {"error": f"File not found: {path}"}
                    
                lines = p.read_text(encoding="utf-8").splitlines()
                content = "\n".join(lines[offset:offset+limit])
                
                return {
                    "path": path,
                    "total_lines": len(lines),
                    "content": content
                }
            except Exception as e:
                return {"error": str(e)}
                
        async def write_file(path: str, content: str) -> Dict:
            """写入文件"""
            try:
                p = Path(path)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
                return {"success": True, "path": path}
            except Exception as e:
                return {"error": str(e)}
                
        async def list_directory(path: str = ".", include_hidden: bool = False) -> Dict:
            """列出目录"""
            try:
                p = Path(path)
                if not p.exists():
                    return {"error": f"Directory not found: {path}"}
                    
                items = []
                for item in p.iterdir():
                    if not include_hidden and item.name.startswith("."):
                        continue
                    items.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file"
                    })
                    
                return {"path": path, "items": items}
            except Exception as e:
                return {"error": str(e)}
                
        async def search_memory(query: str, limit: int = 5) -> Dict:
            """搜索记忆"""
            if not self.memory_store:
                return {"error": "Memory store not initialized"}
                
            results = await self.memory_store.search(query, limit=limit)
            return {"query": query, "results": results}
            
        async def browser_navigate(url: str, action: str = "get_html", **kwargs) -> Dict:
            """
            浏览器操作
            
            Args:
                url: 要访问的 URL
                action: 操作类型 (goto, get_html, screenshot, click, type)
                selector: CSS 选择器 (用于 click/type)
                text: 要输入的文本 (用于 type)
            """
            try:
                # 使用 web_fetch 获取页面内容
                if action in ["goto", "get_html"]:
                    from gogoclaw.utils.web_fetch import fetch_url
                    result = await fetch_url(url)
                    return {
                        "url": url,
                        "action": action,
                        "content": result.get("content", ""),
                        "title": result.get("title", "")
                    }
                elif action == "screenshot":
                    # TODO: 实现截图功能
                    return {
                        "url": url,
                        "action": action,
                        "note": "Screenshot not yet implemented"
                    }
                else:
                    return {
                        "error": f"Unsupported browser action: {action}",
                        "supported_actions": ["goto", "get_html", "screenshot"]
                    }
                    
            except Exception as e:
                return {
                    "error": f"Browser operation failed: {str(e)}"
                }
            
        # 注册处理器
        self.tool_executor.register_handler("execute_command", execute_command)
        self.tool_executor.register_handler("read_file", read_file)
        self.tool_executor.register_handler("write_file", write_file)
        self.tool_executor.register_handler("list_directory", list_directory)
        self.tool_executor.register_handler("search_memory", search_memory)
        self.tool_executor.register_handler("browser_navigate", browser_navigate)
        
    def set_model_client(self, client: ModelClient):
        """设置模型客户端"""
        self._model_client = client
        # 如果客户端支持工具执行，设置工具执行器
        if hasattr(client, 'set_tool_executor'):
            client.set_tool_executor(self.tool_executor)
        
    async def handle_message(self, request: MessageRequest) -> Message:
        """处理消息"""
        # 1. 获取或创建会话
        session = self.session_manager.get_session(request.session_id)
        if not session:
            session = self.session_manager.create_session(
                session_id=request.session_id,
                agent_id=self.config.agent_id,
                channel=request.channel,
                trust_level="main" if "main" in request.session_id else "dm"
            )
            
        # 2. 添加用户消息
        user_message = Message(
            session_id=request.session_id,
            role="user",
            content=request.content,
            channel=request.channel,
            metadata=request.metadata
        )
        session.add_message(user_message)
        
        # 3. 搜索相关记忆
        relevant_memories = []
        if self.memory_store:
            try:
                memories = await self.memory_store.search(
                    request.content, 
                    limit=3
                )
                relevant_memories = [m["content"] for m in memories]
            except Exception as e:
                logger.warning(f"Memory search error: {e}")
                
        # 4. 构建上下文
        config_dict = {
            "agent_id": self.config.agent_id,
            "name": self.config.name,
            "model": {
                "provider": self.config.model_provider,
                "model_name": self.config.model_name
            },
            "system_prompt": self.config.system_prompt,
            "tools": self.config.tools
        }
        
        context = self.context_builder.build(
            agent_config=config_dict,
            session_history=[{"role": m.role, "content": m.content} for m in session.history[:-1]],
            relevant_memories=relevant_memories,
            session_trust_level=session.trust_level
        )
        
        # 5. 调用模型 (支持工具执行循环)
        try:
            response = await self._call_model(context, session)
            response_text = response.content
            
            # 如果有工具调用，处理它们
            max_tool_calls = 10
            tool_call_count = 0
            
            while response.tool_calls and tool_call_count < max_tool_calls:
                tool_call_count += 1
                
                # 将工具调用添加到消息历史
                for tool_call in response.tool_calls:
                    # 添加助手消息（带工具调用）
                    session.add_message(Message(
                        session_id=request.session_id,
                        role="assistant",
                        content=response_text,
                        tool_calls=[tool_call]
                    ))
                    
                    # 执行工具
                    tool_name = tool_call.get("function", {}).get("name")
                    tool_args = tool_call.get("function", {}).get("arguments", {})
                    
                    # 如果 arguments 是字符串，解析为 JSON
                    if isinstance(tool_args, str):
                        try:
                            tool_args = json.loads(tool_args)
                        except:
                            tool_args = {}
                    
                    tool_result = await self.tool_executor.execute(
                        tool_name, 
                        tool_args, 
                        trust_level=session.trust_level
                    )
                    
                    # 添加工具结果到消息历史
                    session.add_message(Message(
                        session_id=request.session_id,
                        role="tool",
                        content=tool_result,
                        tool_call_id=tool_call.get("id")
                    ))
                
                # 再次调用模型，获取下一轮响应
                session_history = [{"role": m.role, "content": m.content} for m in session.history]
                context.chat_history = session_history
                
                response = await self._call_model(context, session)
                response_text = response.content
            
        except Exception as e:
            logger.error(f"Model call error: {e}", exc_info=True)
            # 创建错误响应返回给用户
            error_message = Message(
                session_id=request.session_id,
                role="assistant",
                content=f"抱歉，处理您的请求时发生错误：{str(e)}",
                channel=request.channel
            )
            session.add_message(error_message)
            self.session_manager.save_session(session)
            return error_message
            
        # 7. 添加助手消息
        assistant_message = Message(
            session_id=request.session_id,
            role="assistant",
            content=response_text,
            channel=request.channel
        )
        session.add_message(assistant_message)
        
        # 8. 保存会话
        self.session_manager.save_session(session)
        
        # 9. 存储到记忆
        if self.memory_store:
            try:
                await self.memory_store.add(
                    session_id=request.session_id,
                    role="user",
                    content=request.content
                )
                await self.memory_store.add(
                    session_id=request.session_id,
                    role="assistant",
                    content=response_text
                )
            except Exception as e:
                logger.warning(f"Memory store error: {e}")
                
        return assistant_message
        
    async def _call_model(self, context: Context, session: Session) -> ModelResponse:
        """调用模型"""
        if not self._model_client:
            return ModelResponse(content="Model client not configured")
            
        # 构建消息
        messages = [{"role": "system", "content": context.system_prompt}]
        messages.extend(context.chat_history)
        
        # 获取工具定义
        tools = context.tools if self.config.tools else None
        
        # 调用模型
        response = await self._model_client.chat(
            messages=messages,
            tools=tools,
            model=self.config.model_name
        )
        
        return response

