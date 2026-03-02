"""
GogoClaw 模型客户端测试
测试 7 家模型服务商的客户端初始化、配置和错误处理
"""
import pytest
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestModelClientInitialization:
    """模型客户端初始化测试"""
    
    def test_dashscope_client_init(self):
        """测试阿里云 DashScope 客户端初始化"""
        from gogoclaw.agent.model_client import DashScopeClient
        
        client = DashScopeClient(
            api_key="test-key",
            model="qwen-plus",
            base_url="https://dashscope.aliyuncs.com/api/v1"
        )
        
        assert client.api_key == "test-key"
        assert client.model == "qwen-plus"
        assert "dashscope.aliyuncs.com" in client.base_url
        assert client.timeout == 60
        
    def test_zhipu_client_init(self):
        """测试智谱 AI 客户端初始化"""
        from gogoclaw.agent.model_client import ZhipuClient
        
        client = ZhipuClient(
            api_key="test-key",
            model="glm-4"
        )
        
        assert client.api_key == "test-key"
        assert client.model == "glm-4"
        assert "bigmodel.cn" in client.base_url
        
    def test_kimi_client_init(self):
        """测试 Kimi 客户端初始化"""
        from gogoclaw.agent.model_client import KimiClient
        
        client = KimiClient(
            api_key="test-key",
            model="moonshot-v1-8k"
        )
        
        assert client.api_key == "test-key"
        assert client.model == "moonshot-v1-8k"
        assert "moonshot.cn" in client.base_url
        
    def test_ollama_client_init(self):
        """测试 Ollama 客户端初始化"""
        from gogoclaw.agent.model_client import OllamaClient
        
        client = OllamaClient(
            model="llama3.2",
            base_url="http://localhost:11434"
        )
        
        assert client.model == "llama3.2"
        assert "localhost:11434" in client.base_url
        assert client.timeout == 120  # Ollama 默认超时更长
        
    def test_openai_client_init(self):
        """测试 OpenAI 客户端初始化"""
        from gogoclaw.agent.model_client import OpenAIClient
        
        client = OpenAIClient(
            api_key="test-key",
            model="gpt-4o"
        )
        
        assert client.api_key == "test-key"
        assert client.model == "gpt-4o"
        assert "api.openai.com" in client.base_url
        
    def test_anthropic_client_init(self):
        """测试 Anthropic 客户端初始化"""
        from gogoclaw.agent.model_client import AnthropicClient
        
        client = AnthropicClient(
            api_key="test-key",
            model="claude-3-5-sonnet-20241022"
        )
        
        assert client.api_key == "test-key"
        assert client.model == "claude-3-5-sonnet-20241022"
        assert "anthropic.com" in client.base_url
        
    def test_google_client_init(self):
        """测试 Google 客户端初始化"""
        from gogoclaw.agent.model_client import GoogleClient
        
        client = GoogleClient(
            api_key="test-key",
            model="gemini-1.5-pro"
        )
        
        assert client.api_key == "test-key"
        assert client.model == "gemini-1.5-pro"
        assert "generativelanguage.googleapis.com" in client.base_url


class TestModelClientFactory:
    """模型客户端工厂函数测试"""
    
    def test_create_dashscope_client(self):
        """测试创建 DashScope 客户端"""
        from gogoclaw.agent.model_client import create_model_client, DashScopeClient
        
        client = create_model_client(
            provider="dashscope",
            api_key="test-key",
            model="qwen-plus"
        )
        
        assert isinstance(client, DashScopeClient)
        assert client.model == "qwen-plus"
        
    def test_create_zhipu_client(self):
        """测试创建智谱 AI 客户端"""
        from gogoclaw.agent.model_client import create_model_client, ZhipuClient
        
        client = create_model_client(
            provider="zhipu",
            api_key="test-key",
            model="glm-4"
        )
        
        assert isinstance(client, ZhipuClient)
        
    def test_create_kimi_client(self):
        """测试创建 Kimi 客户端"""
        from gogoclaw.agent.model_client import create_model_client, KimiClient
        
        client = create_model_client(
            provider="kimi",
            api_key="test-key",
            model="moonshot-v1-8k"
        )
        
        assert isinstance(client, KimiClient)
        
    def test_create_ollama_client(self):
        """测试创建 Ollama 客户端"""
        from gogoclaw.agent.model_client import create_model_client, OllamaClient
        
        client = create_model_client(
            provider="ollama",
            model="llama3.2"
        )
        
        assert isinstance(client, OllamaClient)
        
    def test_create_openai_client(self):
        """测试创建 OpenAI 客户端"""
        from gogoclaw.agent.model_client import create_model_client, OpenAIClient
        
        client = create_model_client(
            provider="openai",
            api_key="test-key",
            model="gpt-4o"
        )
        
        assert isinstance(client, OpenAIClient)
        
    def test_create_anthropic_client(self):
        """测试创建 Anthropic 客户端"""
        from gogoclaw.agent.model_client import create_model_client, AnthropicClient
        
        client = create_model_client(
            provider="anthropic",
            api_key="test-key",
            model="claude-3-5-sonnet-20241022"
        )
        
        assert isinstance(client, AnthropicClient)
        
    def test_create_google_client(self):
        """测试创建 Google 客户端"""
        from gogoclaw.agent.model_client import create_model_client, GoogleClient
        
        client = create_model_client(
            provider="google",
            api_key="test-key",
            model="gemini-1.5-pro"
        )
        
        assert isinstance(client, GoogleClient)
        
    def test_create_client_with_aliases(self):
        """测试使用别名创建客户端"""
        from gogoclaw.agent.model_client import create_model_client
        
        # 测试别名
        aliyun_client = create_model_client(provider="aliyun", api_key="test")
        assert aliyun_client.__class__.__name__ == "DashScopeClient"
        
        glm_client = create_model_client(provider="glm", api_key="test")
        assert glm_client.__class__.__name__ == "ZhipuClient"
        
        moonshot_client = create_model_client(provider="moonshot", api_key="test")
        assert moonshot_client.__class__.__name__ == "KimiClient"
        
        claude_client = create_model_client(provider="claude", api_key="test")
        assert claude_client.__class__.__name__ == "AnthropicClient"
        
        gemini_client = create_model_client(provider="gemini", api_key="test")
        assert gemini_client.__class__.__name__ == "GoogleClient"
        
    def test_create_client_invalid_provider(self):
        """测试无效提供商"""
        from gogoclaw.agent.model_client import create_model_client
        
        with pytest.raises(ValueError, match="Unknown provider"):
            create_model_client(provider="invalid_provider", api_key="test")


class TestModelResponse:
    """模型响应测试"""
    
    def test_model_response_basic(self):
        """测试基本响应"""
        from gogoclaw.agent.model_client import ModelResponse
        
        response = ModelResponse(
            content="Hello, world!",
            finish_reason="stop"
        )
        
        assert response.content == "Hello, world!"
        assert response.finish_reason == "stop"
        assert response.tool_calls is None
        assert response.usage is None
        
    def test_model_response_with_tool_calls(self):
        """测试带工具调用的响应"""
        from gogoclaw.agent.model_client import ModelResponse
        
        tool_call = {
            "id": "call_123",
            "function": {
                "name": "execute_command",
                "arguments": '{"command": "ls -la"}'
            }
        }
        
        response = ModelResponse(
            content="Let me run that command.",
            tool_calls=[tool_call],
            finish_reason="tool_calls"
        )
        
        assert response.content == "Let me run that command."
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["id"] == "call_123"
        
    def test_model_response_with_usage(self):
        """测试带使用量统计的响应"""
        from gogoclaw.agent.model_client import ModelResponse
        
        response = ModelResponse(
            content="Response text",
            usage={
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        )
        
        assert response.usage["total_tokens"] == 150


class TestMockClient:
    """模拟客户端测试"""
    
    def test_mock_client_chat(self):
        """测试模拟客户端聊天"""
        from gogoclaw.agent.model_client import MockClient, ModelResponse
        
        client = MockClient("Mock response")
        
        loop = asyncio.new_event_loop()
        try:
            response = loop.run_until_complete(
                client.chat([{"role": "user", "content": "Hi"}])
            )
            assert isinstance(response, ModelResponse)
            assert response.content == "Mock response"
        finally:
            loop.close()
            
    def test_mock_client_with_tool_calls(self):
        """测试模拟客户端带工具调用"""
        from gogoclaw.agent.model_client import MockClient, ModelResponse
        
        tool_calls = [{"id": "call_1", "function": {"name": "test_tool"}}]
        client = MockClient("Response", tool_calls=tool_calls)
        
        loop = asyncio.new_event_loop()
        try:
            response = loop.run_until_complete(
                client.chat([{"role": "user", "content": "Hi"}])
            )
            assert response.tool_calls == tool_calls
        finally:
            loop.close()


class TestErrorHandling:
    """错误处理测试"""
    
    def test_client_error_response(self):
        """测试客户端错误响应格式"""
        from gogoclaw.agent.model_client import ModelResponse
        
        # 模拟错误响应
        error_response = ModelResponse(
            content="Error: Connection failed",
            finish_reason="error"
        )
        
        assert "Error" in error_response.content
        assert error_response.finish_reason == "error"
        
    def test_base_client_not_implemented(self):
        """测试基类未实现方法"""
        from gogoclaw.agent.model_client import BaseModelClient
        
        client = BaseModelClient()
        
        with pytest.raises(NotImplementedError):
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(
                    client.chat([{"role": "user", "content": "Hi"}])
                )
            finally:
                loop.close()


class TestEnvConfigLoading:
    """环境变量配置加载测试"""
    
    def test_settings_from_env(self):
        """测试从环境变量加载配置"""
        import os
        from gogoclaw.config.settings import Settings, init_settings
        
        # 保存原值
        original = os.environ.get("GOGOCLAW_AGENTS__MAIN__MODEL__PROVIDER")
        
        try:
            # 设置环境变量
            os.environ["GOGOCLAW_AGENTS__MAIN__MODEL__PROVIDER"] = "openai"
            os.environ["GOGOCLAW_AGENTS__MAIN__MODEL__MODEL_NAME"] = "gpt-4o"
            
            # 重新初始化设置
            settings = init_settings()
            
            assert settings.agents["main"].model.provider == "openai"
            assert settings.agents["main"].model.model_name == "gpt-4o"
        finally:
            # 恢复原值
            if original:
                os.environ["GOGOCLAW_AGENTS__MAIN__MODEL__PROVIDER"] = original
            elif "GOGOCLAW_AGENTS__MAIN__MODEL__PROVIDER" in os.environ:
                del os.environ["GOGOCLAW_AGENTS__MAIN__MODEL__PROVIDER"]
