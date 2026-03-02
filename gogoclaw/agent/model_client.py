"""
GogoClaw 模型客户端 - 支持国内外主流模型提供商

支持:
- 国内：阿里云通义千问、智谱 AI、Kimi(月之暗面)
- 本地：Ollama
- 国外：OpenAI、Anthropic、Google
"""
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


@dataclass
class ModelResponse:
    """模型响应"""
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    finish_reason: str = "stop"
    usage: Optional[Dict[str, int]] = None


class BaseModelClient:
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


class DashScopeClient(BaseModelClient):
    """阿里云通义千问客户端 (DashScope)"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "qwen-plus",
        base_url: str = "https://dashscope.aliyuncs.com/api/v1",
        **kwargs
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = kwargs.get("timeout", 60)
        
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """调用通义千问 API"""
        model = model or self.model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        # 添加工具支持
        if tools:
            payload["tools"] = tools
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/services/aigc/text-generation/generation",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                # 解析响应
                if "output" in data and "choices" in data["output"]:
                    choice = data["output"]["choices"][0]
                    message = choice.get("message", {})
                    
                    return ModelResponse(
                        content=message.get("content", ""),
                        tool_calls=message.get("tool_calls"),
                        finish_reason=choice.get("finish_reason", "stop"),
                        usage=data.get("usage")
                    )
                else:
                    return ModelResponse(
                        content="",
                        finish_reason="error"
                    )
                    
        except Exception as e:
            logger.error(f"DashScope API error: {e}")
            return ModelResponse(
                content=f"Error: {str(e)}",
                finish_reason="error"
            )


class ZhipuClient(BaseModelClient):
    """智谱 AI 客户端 (GLM)"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "glm-4",
        base_url: str = "https://open.bigmodel.cn/api/paas/v4",
        **kwargs
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = kwargs.get("timeout", 60)
        
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """调用智谱 AI API"""
        model = model or self.model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        if tools:
            payload["tools"] = tools
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {})
                
                return ModelResponse(
                    content=message.get("content", ""),
                    tool_calls=message.get("tool_calls"),
                    finish_reason=choice.get("finish_reason", "stop"),
                    usage=data.get("usage")
                )
                    
        except Exception as e:
            logger.error(f"Zhipu API error: {e}")
            return ModelResponse(
                content=f"Error: {str(e)}",
                finish_reason="error"
            )


class KimiClient(BaseModelClient):
    """Kimi (月之暗面) 客户端"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "moonshot-v1-8k",
        base_url: str = "https://api.moonshot.cn/v1",
        **kwargs
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = kwargs.get("timeout", 60)
        
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """调用 Kimi API"""
        model = model or self.model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        if tools:
            payload["tools"] = tools
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {})
                
                return ModelResponse(
                    content=message.get("content", ""),
                    tool_calls=message.get("tool_calls"),
                    finish_reason=choice.get("finish_reason", "stop"),
                    usage=data.get("usage")
                )
                    
        except Exception as e:
            logger.error(f"Kimi API error: {e}")
            return ModelResponse(
                content=f"Error: {str(e)}",
                finish_reason="error"
            )


class OllamaClient(BaseModelClient):
    """Ollama 本地模型客户端"""
    
    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        **kwargs
    ):
        self.model = model
        self.base_url = base_url
        self.timeout = kwargs.get("timeout", 120)
        
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """调用 Ollama API"""
        model = model or self.model
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        # Ollama 工具支持 (v0.1.30+)
        if tools:
            payload["tools"] = tools
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                message = data.get("message", {})
                
                return ModelResponse(
                    content=message.get("content", ""),
                    tool_calls=message.get("tool_calls"),
                    finish_reason="stop" if data.get("done") else "length",
                    usage=data.get("prompt_eval_count", {})
                )
                    
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return ModelResponse(
                content=f"Error: {str(e)}",
                finish_reason="error"
            )


class OpenAIClient(BaseModelClient):
    """OpenAI 客户端"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        base_url: Optional[str] = None,
        **kwargs
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://api.openai.com/v1"
        self.timeout = kwargs.get("timeout", 60)
        
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """调用 OpenAI API"""
        model = model or self.model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        if tools:
            payload["tools"] = tools
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {})
                
                return ModelResponse(
                    content=message.get("content", ""),
                    tool_calls=message.get("tool_calls"),
                    finish_reason=choice.get("finish_reason", "stop"),
                    usage=data.get("usage")
                )
                    
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return ModelResponse(
                content=f"Error: {str(e)}",
                finish_reason="error"
            )


class AnthropicClient(BaseModelClient):
    """Anthropic (Claude) 客户端"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        base_url: str = "https://api.anthropic.com",
        **kwargs
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = kwargs.get("timeout", 60)
        
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """调用 Anthropic API"""
        model = model or self.model
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # 转换消息格式 (Anthropic 格式)
        system_message = ""
        anthropic_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        payload = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": 4096,
            "stream": False
        }
        
        if system_message:
            payload["system"] = system_message
            
        if tools:
            payload["tools"] = tools
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/messages",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                # 解析响应
                content_blocks = data.get("content", [])
                text_content = ""
                tool_calls = []
                
                for block in content_blocks:
                    if block.get("type") == "text":
                        text_content += block.get("text", "")
                    elif block.get("type") == "tool_use":
                        tool_calls.append({
                            "id": block.get("id"),
                            "function": {
                                "name": block.get("name"),
                                "arguments": json.dumps(block.get("input", {}))
                            }
                        })
                
                return ModelResponse(
                    content=text_content,
                    tool_calls=tool_calls if tool_calls else None,
                    finish_reason=data.get("stop_reason", "stop"),
                    usage=data.get("usage")
                )
                    
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return ModelResponse(
                content=f"Error: {str(e)}",
                finish_reason="error"
            )


class GoogleClient(BaseModelClient):
    """Google (Gemini) 客户端"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-pro",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        **kwargs
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = kwargs.get("timeout", 60)
        
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """调用 Google Gemini API"""
        model = model or self.model
        
        # 转换消息格式 (Gemini 格式)
        contents = []
        system_instruction = None
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            else:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
        
        payload = {
            "contents": contents
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
        
        # 工具支持
        if tools:
            payload["tools"] = [{
                "functionDeclarations": [
                    {
                        "name": t["function"]["name"],
                        "description": t["function"]["description"],
                        "parameters": t["function"]["parameters"]
                    }
                    for t in tools
                ]
            }]
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/models/{model}:generateContent",
                    params={"key": self.api_key},
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                # 解析响应
                candidates = data.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    
                    text_content = ""
                    tool_calls = []
                    
                    for part in parts:
                        if "text" in part:
                            text_content += part["text"]
                        elif "functionCall" in part:
                            tool_calls.append({
                                "id": part["functionCall"].get("name", ""),
                                "function": {
                                    "name": part["functionCall"].get("name"),
                                    "arguments": json.dumps(part["functionCall"].get("args", {}))
                                }
                            })
                    
                    return ModelResponse(
                        content=text_content,
                        tool_calls=tool_calls if tool_calls else None,
                        finish_reason=candidates[0].get("finishReason", "stop")
                    )
                else:
                    return ModelResponse(
                        content="",
                        finish_reason="error"
                    )
                    
        except Exception as e:
            logger.error(f"Google API error: {e}")
            return ModelResponse(
                content=f"Error: {str(e)}",
                finish_reason="error"
            )


def create_model_client(
    provider: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> BaseModelClient:
    """
    创建模型客户端工厂函数
    
    Args:
        provider: 模型提供商 (dashscope, zhipu, kimi, ollama, openai, anthropic, google)
        api_key: API Key
        model: 模型名称
        base_url: 自定义 API 地址
        
    Returns:
        BaseModelClient: 模型客户端实例
    """
    provider = provider.lower()
    
    clients = {
        "dashscope": DashScopeClient,
        "aliyun": DashScopeClient,
        "zhipu": ZhipuClient,
        "glm": ZhipuClient,
        "kimi": KimiClient,
        "moonshot": KimiClient,
        "ollama": OllamaClient,
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "claude": AnthropicClient,
        "google": GoogleClient,
        "gemini": GoogleClient,
    }
    
    client_class = clients.get(provider)
    if not client_class:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(clients.keys())}")
    
    # 准备参数
    init_kwargs = {"api_key": api_key} if api_key else {}
    if model:
        init_kwargs["model"] = model
    if base_url:
        init_kwargs["base_url"] = base_url
    init_kwargs.update(kwargs)
    
    return client_class(**init_kwargs)
