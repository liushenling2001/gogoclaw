"""
GogoClaw 模型客户端 - LangChain 集成
"""
import json
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelResponse:
    """模型响应"""
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    finish_reason: str = "stop"


class ModelClient:
    """模型客户端基类"""
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: str = "gpt-4o",
        **kwargs
    ) -> ModelResponse:
        """发送聊天请求"""
        raise NotImplementedError


class LangChainClient(ModelClient):
    """LangChain 模型客户端"""
    
    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
        self._tool_executor = None
        
    def _init_client(self):
        """初始化 LangChain 客户端"""
        if self._client is not None:
            return
            
        try:
            if self.provider == "openai":
                from langchain_openai import ChatOpenAI
                self._client = ChatOpenAI(
                    model=self.model,
                    api_key=self.api_key,
                    base_url=self.base_url,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    streaming=True
                )
            elif self.provider == "anthropic":
                from langchain_anthropic import ChatAnthropic
                self._client = ChatAnthropic(
                    model=self.model,
                    anthropic_api_key=self.api_key,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            elif self.provider == "google":
                from langchain_google_genai import ChatGoogleGenerativeAI
                self._client = ChatGoogleGenerativeAI(
                    model=self.model,
                    google_api_key=self.api_key,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            elif self.provider == "ollama":
                from langchain_ollama import ChatOllama
                self._client = ChatOllama(
                    model=self.model,
                    base_url=self.base_url or "http://localhost:11434",
                    temperature=self.temperature
                )
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
                
            logger.info(f"Initialized {self.provider} client with model {self.model}")
            
        except ImportError as e:
            logger.warning(f"LangChain provider not installed: {e}")
            self._client = None
            
    def set_tool_executor(self, executor):
        """设置工具执行器"""
        self._tool_executor = executor
        
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: str = "gpt-4o",
        max_tool_calls: int = 10,
        **kwargs
    ) -> ModelResponse:
        """
        发送聊天请求，支持工具调用循环
        
        Args:
            messages: 消息列表
            tools: 工具定义列表
            model: 模型名称
            max_tool_calls: 最大工具调用次数
            
        Returns:
            ModelResponse: 包含内容或工具调用
        """
        self._init_client()
        
        if not self._client:
            # Fallback: 返回模拟响应
            return ModelResponse(
                content="Model client not initialized. Please install langchain packages.",
                finish_reason="error"
            )
            
        # 转换消息格式
        from langchain.schema import HumanMessage, SystemMessage, AIMessage, ToolMessage
        
        lc_messages = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                # 检查是否有工具调用
                if msg.get("tool_calls"):
                    # 转换为 AIMessage with tool calls
                    from langchain.schema import AIMessage
                    lc_messages.append(AIMessage(
                        content=content,
                        additional_kwargs={"tool_calls": msg.get("tool_calls")}
                    ))
                else:
                    lc_messages.append(AIMessage(content=content))
            elif role == "tool":
                lc_messages.append(ToolMessage(
                    content=content,
                    tool_call_id=msg.get("tool_call_id", "")
                ))
        
        # 绑定工具 (如果有)
        from langchain.tools import Tool
        from langchain.agents import AgentExecutor
        
        if tools and self._tool_executor:
            # 将工具定义转换为 LangChain 工具
            langchain_tools = []
            for tool_def in tools:
                func_def = tool_def.get("function", {})
                tool_name = func_def.get("name")
                tool_desc = func_def.get("description")
                
                # 创建异步工具函数
                async def create_tool_handler(name: str):
                    async def handler(**kwargs):
                        return await self._tool_executor.execute(name, kwargs, trust_level="dm")
                    return handler
                    
                langchain_tools.append(Tool(
                    name=tool_name,
                    description=tool_desc,
                    func=None,  # 异步执行
                    coroutine=create_tool_handler(tool_name)
                ))
                
            # 使用 LangChain Agent
            from langchain.agents import create_openai_functions_agent
            
            agent = create_openai_functions_agent(self._client, langchain_tools, lc_messages)
            agent_executor = AgentExecutor(
                agent=agent,
                tools=langchain_tools,
                max_iterations=max_tool_calls,
                verbose=True
            )
            
            try:
                result = await agent_executor.ainvoke({})
                return ModelResponse(
                    content=result.get("output", ""),
                    finish_reason="agent_finish"
                )
            except Exception as e:
                logger.error(f"Agent execution error: {e}")
                return ModelResponse(
                    content=f"Error: {str(e)}",
                    finish_reason="error"
                )
        
        # 直接调用模型 (无工具)
        try:
            response = await self._client.agenerate([lc_messages])
            content = response.generations[0][0].text
            
            return ModelResponse(
                content=content,
                finish_reason="stop"
            )
        except Exception as e:
            logger.error(f"Model call error: {e}")
            return ModelResponse(
                content=f"Error: {str(e)}",
                finish_reason="error"
            )


class MockClient(ModelClient):
    """模拟客户端，用于测试"""
    
    def __init__(self, response_text: str = "Hello from mock client"):
        self.response_text = response_text
        
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: str = "mock",
        **kwargs
    ) -> ModelResponse:
        """返回模拟响应"""
        return ModelResponse(
            content=self.response_text,
            finish_reason="stop"
        )


def create_model_client(
    provider: str = "openai",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: str = "gpt-4o",
    **kwargs
) -> ModelClient:
    """
    创建模型客户端工厂函数
    
    Args:
        provider: 模型提供商 (openai, anthropic, google, ollama)
        api_key: API Key
        base_url: 自定义 API 地址
        model: 模型名称
        
    Returns:
        ModelClient: 模型客户端实例
    """
    if provider == "mock":
        return MockClient(kwargs.get("mock_response", "Mock response"))
        
    return LangChainClient(
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        model=model,
        **kwargs
    )
