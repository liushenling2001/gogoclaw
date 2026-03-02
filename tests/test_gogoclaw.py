"""
GogoClaw 测试套件
"""
import pytest
import asyncio
from pathlib import Path
import tempfile
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfig:
    """配置模块测试"""
    
    def test_settings_creation(self):
        """测试设置创建"""
        from gogoclaw.config.settings import Settings, get_settings
        
        settings = Settings()
        assert settings.gateway.host == "127.0.0.1"
        assert settings.gateway.port == 16888
        assert "main" in settings.agents
        
    def test_agent_config(self):
        """测试 Agent 配置"""
        from gogoclaw.config.settings import AgentConfig, ModelConfig
        
        agent = AgentConfig()
        assert agent.agent_id == "main"
        assert agent.model.model_name == "gpt-4o"
        assert agent.sandbox_enabled is True
        
    def test_get_settings_singleton(self):
        """测试单例模式"""
        from gogoclaw.config.settings import get_settings
        
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2


class TestProtocol:
    """协议模块测试"""
    
    def test_message_creation(self):
        """测试消息创建"""
        from gogoclaw.gateway.protocol import Message
        
        msg = Message(
            session_id="test-session",
            role="user",
            content="Hello"
        )
        assert msg.session_id == "test-session"
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.id is not None
        
    def test_message_request(self):
        """测试消息请求"""
        from gogoclaw.gateway.protocol import MessageRequest
        
        req = MessageRequest(
            session_id="test-session",
            content="Hello"
        )
        assert req.session_id == "test-session"
        assert req.channel == "webui"  # 默认值


class TestSecurity:
    """安全模块测试"""
    
    def test_whitelist(self):
        """测试白名单"""
        from gogoclaw.gateway.security import AccessControl
        
        ac = AccessControl()
        ac.add_whitelist("user123")
        
        assert ac.is_whitelisted("user123") is True
        assert ac.is_whitelisted("user456") is False
        
    def test_dm_policy(self):
        """测试 DM 策略"""
        from gogoclaw.gateway.security import AccessControl
        
        ac = AccessControl()
        ac.set_policy(dm_policy="deny")
        
        allowed, reason = ac.check_access("telegram", "user123", is_group=False)
        assert allowed is False
        assert reason == "dm_deny"
        
    def test_group_policy_mentioned(self):
        """测试群聊 @提及策略"""
        from gogoclaw.gateway.security import AccessControl
        
        ac = AccessControl()
        
        # 未提及
        allowed, reason = ac.check_access("telegram", "user123", is_group=True, is_mentioned=False)
        assert allowed is False
        assert reason == "group_not_mentioned"
        
        # 已提及
        allowed, reason = ac.check_access("telegram", "user123", is_group=True, is_mentioned=True)
        assert allowed is True
        assert reason == "group_mentioned"


class TestRouter:
    """路由模块测试"""
    
    def test_session_resolver_main(self):
        """测试主会话解析"""
        from gogoclaw.gateway.router import SessionResolver
        
        session_id = SessionResolver.resolve_session_id(
            channel="telegram",
            sender="self",
            is_group=False
        )
        assert session_id == "agent:main:main"
        
    def test_session_resolver_dm(self):
        """测试 DM 会话解析"""
        from gogoclaw.gateway.router import SessionResolver
        
        session_id = SessionResolver.resolve_session_id(
            channel="telegram",
            sender="user123",
            is_group=False
        )
        assert "telegram" in session_id
        assert ":dm:" in session_id
        
    def test_session_resolver_group(self):
        """测试群聊会话解析"""
        from gogoclaw.gateway.router import SessionResolver
        
        session_id = SessionResolver.resolve_session_id(
            channel="telegram",
            sender="user123",
            is_group=True,
            group_id="group456"
        )
        assert "telegram" in session_id
        assert ":group:" in session_id
        
    def test_get_trust_level(self):
        """测试信任级别"""
        from gogoclaw.gateway.router import SessionResolver
        
        assert SessionResolver.get_trust_level("agent:main:main") == "main"
        assert SessionResolver.get_trust_level("agent:main:telegram:dm:123") == "dm"
        assert SessionResolver.get_trust_level("agent:main:telegram:group:456") == "group"


class TestSession:
    """会话模块测试"""
    
    @pytest.fixture
    def temp_dir(self):
        """临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
            
    def test_session_creation(self, temp_dir):
        """测试会话创建"""
        from gogoclaw.agent.session import SessionManager
        
        manager = SessionManager(temp_dir)
        session = manager.create_session(
            session_id="test-session",
            agent_id="main",
            channel="webui",
            trust_level="dm"
        )
        
        assert session.session_id == "test-session"
        assert session.agent_id == "main"
        assert session.trust_level == "dm"
        
    def test_session_save_load(self, temp_dir):
        """测试会话保存和加载"""
        from gogoclaw.agent.session import SessionManager, Session
        from gogoclaw.gateway.protocol import Message
        
        manager = SessionManager(temp_dir)
        
        # 创建并添加消息
        session = manager.create_session("test-session")
        session.add_message(Message(
            session_id="test-session",
            role="user",
            content="Hello"
        ))
        
        manager.save_session(session)
        
        # 重新加载
        loaded = manager.get_session("test-session")
        assert loaded is not None
        assert len(loaded.history) == 1
        assert loaded.history[0].content == "Hello"


class TestTools:
    """工具模块测试"""
    
    def test_builtin_tools(self):
        """测试内置工具定义"""
        from gogoclaw.agent.tools import get_builtin_tools
        
        tools = get_builtin_tools()
        assert len(tools) > 0
        
        # 检查工具名称
        tool_names = [t["function"]["name"] for t in tools]
        assert "execute_command" in tool_names
        assert "read_file" in tool_names
        assert "write_file" in tool_names
        
    def test_tool_registry(self):
        """测试工具注册表"""
        from gogoclaw.agent.tools import ToolRegistry, register_tool
        
        registry = ToolRegistry()
        
        def dummy_func(x: str) -> str:
            return x
            
        registry.register("dummy", dummy_func, {
            "type": "function",
            "function": {
                "name": "dummy",
                "description": "A dummy tool",
                "parameters": {"type": "object"}
            }
        })
        
        assert registry.get_tool("dummy") is not None
        assert registry.get_definition("dummy") is not None


class TestModelClient:
    """模型客户端测试"""
    
    def test_mock_client(self):
        """测试模拟客户端"""
        from gogoclaw.agent.model_client import MockClient, ModelResponse
        
        client = MockClient("Test response")
        
        # 同步运行
        import asyncio
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(
            client.chat([{"role": "user", "content": "Hi"}])
        )
        loop.close()
        
        assert isinstance(response, ModelResponse)
        assert response.content == "Test response"
        
    def test_create_model_client(self):
        """测试模型客户端工厂"""
        from gogoclaw.agent.model_client import create_model_client, MockClient
        
        # 创建模拟客户端
        client = create_model_client("mock", mock_response="Hello")
        assert isinstance(client, MockClient)


class TestMemory:
    """记忆模块测试"""
    
    @pytest.fixture
    def temp_dir(self):
        """临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
            
    @pytest.mark.asyncio
    async def test_memory_add(self, temp_dir):
        """测试添加记忆"""
        from gogoclaw.memory.store import MemoryStore
        
        store = MemoryStore(temp_dir, vector_enabled=False)
        
        memory_id = await store.add(
            session_id="test-session",
            role="user",
            content="Hello world"
        )
        
        assert memory_id is not None
        
    @pytest.mark.asyncio
    async def test_memory_search(self, temp_dir):
        """测试记忆搜索"""
        from gogoclaw.memory.store import MemoryStore
        
        store = MemoryStore(temp_dir, vector_enabled=False)
        
        # 添加记忆
        await store.add("test-session", "user", "Hello world")
        await store.add("test-session", "assistant", "Hi there")
        
        # 搜索
        results = await store.search("Hello")
        
        assert len(results) > 0


# 运行所有测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
