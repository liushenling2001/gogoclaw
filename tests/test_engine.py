"""
GogoClaw 引擎测试
测试 Agent 引擎的核心功能
"""
import pytest
import asyncio
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAgentConfig:
    """Agent 配置测试"""
    
    def test_agent_config_creation(self):
        """测试 Agent 配置创建"""
        from gogoclaw.agent.engine import AgentConfig
        
        config = AgentConfig(
            agent_id="main",
            name="GogoClaw",
            model_provider="openai",
            model_name="gpt-4o",
            system_prompt="You are a helpful assistant.",
            tools=["command", "browser"],
            sandbox_enabled=True,
            memory_enabled=True
        )
        
        assert config.agent_id == "main"
        assert config.name == "GogoClaw"
        assert config.model_provider == "openai"
        assert config.model_name == "gpt-4o"
        assert config.sandbox_enabled is True
        
    def test_agent_config_from_dict(self):
        """测试从字典创建 Agent 配置"""
        from gogoclaw.agent.engine import AgentConfig
        
        data = {
            "agent_id": "test-agent",
            "name": "Test Bot",
            "model": {
                "provider": "anthropic",
                "model_name": "claude-3-5-sonnet"
            },
            "system_prompt": "Test prompt",
            "tools": ["file"],
            "sandbox_enabled": False,
            "memory_enabled": False
        }
        
        config = AgentConfig.from_dict(data)
        
        assert config.agent_id == "test-agent"
        assert config.name == "Test Bot"
        assert config.model_provider == "anthropic"
        assert config.model_name == "claude-3-5-sonnet"
        assert config.sandbox_enabled is False


class TestToolExecutor:
    """工具执行器测试"""
    
    def test_tool_executor_creation(self):
        """测试工具执行器创建"""
        from gogoclaw.agent.engine import ToolExecutor
        
        executor = ToolExecutor(sandbox_enabled=True)
        assert executor.sandbox_enabled is True
        assert len(executor._tool_handlers) == 0
        
    def test_tool_executor_register_handler(self):
        """测试注册工具处理器"""
        from gogoclaw.agent.engine import ToolExecutor
        
        executor = ToolExecutor()
        
        def dummy_tool(x: str) -> str:
            return x
            
        executor.register_handler("dummy", dummy_tool)
        
        assert "dummy" in executor._tool_handlers
        
    @pytest.mark.asyncio
    async def test_tool_executor_execute(self):
        """测试执行工具"""
        from gogoclaw.agent.engine import ToolExecutor
        
        executor = ToolExecutor(sandbox_enabled=False)
        
        async def echo_tool(message: str) -> dict:
            return {"echo": message}
            
        executor.register_handler("echo", echo_tool)
        
        result = await executor.execute("echo", {"message": "Hello"})
        
        assert '"echo": "Hello"' in result
        
    @pytest.mark.asyncio
    async def test_tool_executor_unknown_tool(self):
        """测试执行未知工具"""
        from gogoclaw.agent.engine import ToolExecutor
        
        executor = ToolExecutor()
        
        result = await executor.execute("unknown_tool", {})
        
        assert "error" in result
        assert "Unknown tool" in result
        
    @pytest.mark.asyncio
    async def test_tool_executor_error_handling(self):
        """测试工具执行错误处理"""
        from gogoclaw.agent.engine import ToolExecutor
        
        executor = ToolExecutor(sandbox_enabled=False)
        
        async def failing_tool() -> dict:
            raise ValueError("Test error")
            
        executor.register_handler("failing", failing_tool)
        
        result = await executor.execute("failing", {})
        
        assert "error" in result
        assert "Test error" in result


class TestAgentEngine:
    """Agent 引擎测试"""
    
    @pytest.fixture
    def temp_storage(self):
        """临时存储目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
            
    def test_agent_engine_creation(self, temp_storage):
        """测试 Agent 引擎创建"""
        from gogoclaw.agent.engine import AgentEngine, AgentConfig
        
        config = AgentConfig(
            agent_id="main",
            name="GogoClaw",
            model_provider="openai",
            model_name="gpt-4o",
            system_prompt="Test",
            tools=[],
            sandbox_enabled=False,
            memory_enabled=False
        )
        
        engine = AgentEngine(
            agent_config=config,
            storage_dir=temp_storage
        )
        
        assert engine.config.agent_id == "main"
        assert engine.storage_dir == temp_storage
        assert engine._model_client is None
        
    def test_agent_engine_register_builtin_tools(self, temp_storage):
        """测试注册内置工具"""
        from gogoclaw.agent.engine import AgentEngine, AgentConfig
        
        config = AgentConfig(
            agent_id="main",
            name="GogoClaw",
            model_provider="openai",
            model_name="gpt-4o",
            system_prompt="Test",
            tools=["command", "file"],
            sandbox_enabled=False,
            memory_enabled=False
        )
        
        engine = AgentEngine(
            agent_config=config,
            storage_dir=temp_storage
        )
        
        # 检查内置工具已注册
        handlers = engine.tool_executor._tool_handlers
        assert "execute_command" in handlers
        assert "read_file" in handlers
        assert "write_file" in handlers
        assert "list_directory" in handlers
        
    def test_agent_engine_set_model_client(self, temp_storage):
        """测试设置模型客户端"""
        from gogoclaw.agent.engine import AgentEngine, AgentConfig
        from gogoclaw.agent.model_client import MockClient
        
        config = AgentConfig(
            agent_id="main",
            name="GogoClaw",
            model_provider="mock",
            model_name="mock-model",
            system_prompt="Test",
            tools=[],
            sandbox_enabled=False,
            memory_enabled=False
        )
        
        engine = AgentEngine(
            agent_config=config,
            storage_dir=temp_storage
        )
        
        mock_client = MockClient("Test response")
        engine.set_model_client(mock_client)
        
        assert engine._model_client is mock_client


class TestBuiltInTools:
    """内置工具测试"""
    
    @pytest.fixture
    def temp_dir(self):
        """临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
            
    @pytest.mark.asyncio
    async def test_execute_command(self, temp_dir):
        """测试执行命令"""
        from gogoclaw.agent.engine import AgentEngine, AgentConfig
        
        config = AgentConfig(
            agent_id="main",
            name="GogoClaw",
            model_provider="openai",
            model_name="gpt-4o",
            system_prompt="Test",
            tools=["command"],
            sandbox_enabled=False,
            memory_enabled=False
        )
        
        engine = AgentEngine(config, temp_dir)
        
        # 执行简单命令
        result = await engine.tool_executor.execute(
            "execute_command",
            {"command": "echo 'Hello World'"}
        )
        
        assert "Hello World" in result
        
    @pytest.mark.asyncio
    async def test_execute_command_blocked(self, temp_dir):
        """测试危险命令被阻止"""
        from gogoclaw.agent.engine import AgentEngine, AgentConfig
        
        config = AgentConfig(
            agent_id="main",
            name="GogoClaw",
            model_provider="openai",
            model_name="gpt-4o",
            system_prompt="Test",
            tools=["command"],
            sandbox_enabled=False,
            memory_enabled=False
        )
        
        engine = AgentEngine(config, temp_dir)
        
        # 尝试执行危险命令
        result = await engine.tool_executor.execute(
            "execute_command",
            {"command": "rm -rf /"}
        )
        
        assert "Dangerous command blocked" in result
        
    @pytest.mark.asyncio
    async def test_read_file(self, temp_dir):
        """测试读取文件"""
        from gogoclaw.agent.engine import AgentEngine, AgentConfig
        
        # 创建测试文件
        test_file = temp_dir / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3")
        
        config = AgentConfig(
            agent_id="main",
            name="GogoClaw",
            model_provider="openai",
            model_name="gpt-4o",
            system_prompt="Test",
            tools=["file"],
            sandbox_enabled=False,
            memory_enabled=False
        )
        
        engine = AgentEngine(config, temp_dir)
        
        result = await engine.tool_executor.execute(
            "read_file",
            {"path": str(test_file)}
        )
        
        assert "Line 1" in result
        assert "total_lines" in result
        
    @pytest.mark.asyncio
    async def test_read_file_not_found(self, temp_dir):
        """测试读取不存在的文件"""
        from gogoclaw.agent.engine import AgentEngine, AgentConfig
        
        config = AgentConfig(
            agent_id="main",
            name="GogoClaw",
            model_provider="openai",
            model_name="gpt-4o",
            system_prompt="Test",
            tools=["file"],
            sandbox_enabled=False,
            memory_enabled=False
        )
        
        engine = AgentEngine(config, temp_dir)
        
        result = await engine.tool_executor.execute(
            "read_file",
            {"path": "/nonexistent/file.txt"}
        )
        
        assert "error" in result
        assert "File not found" in result
        
    @pytest.mark.asyncio
    async def test_write_file(self, temp_dir):
        """测试写入文件"""
        from gogoclaw.agent.engine import AgentEngine, AgentConfig
        
        config = AgentConfig(
            agent_id="main",
            name="GogoClaw",
            model_provider="openai",
            model_name="gpt-4o",
            system_prompt="Test",
            tools=["file"],
            sandbox_enabled=False,
            memory_enabled=False
        )
        
        engine = AgentEngine(config, temp_dir)
        
        test_file = temp_dir / "output.txt"
        result = await engine.tool_executor.execute(
            "write_file",
            {"path": str(test_file), "content": "Test content"}
        )
        
        assert "success" in result
        assert test_file.exists()
        assert test_file.read_text() == "Test content"
        
    @pytest.mark.asyncio
    async def test_list_directory(self, temp_dir):
        """测试列出目录"""
        from gogoclaw.agent.engine import AgentEngine, AgentConfig
        
        # 创建测试文件
        (temp_dir / "file1.txt").write_text("test")
        (temp_dir / "file2.txt").write_text("test")
        
        config = AgentConfig(
            agent_id="main",
            name="GogoClaw",
            model_provider="openai",
            model_name="gpt-4o",
            system_prompt="Test",
            tools=["file"],
            sandbox_enabled=False,
            memory_enabled=False
        )
        
        engine = AgentEngine(config, temp_dir)
        
        result = await engine.tool_executor.execute(
            "list_directory",
            {"path": str(temp_dir)}
        )
        
        assert "items" in result
        assert "file1.txt" in result
        assert "file2.txt" in result


class TestMessageHandling:
    """消息处理测试"""
    
    @pytest.fixture
    def temp_storage(self):
        """临时存储目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
            
    @pytest.mark.asyncio
    async def test_handle_message_basic(self, temp_storage):
        """测试基本消息处理"""
        from gogoclaw.agent.engine import AgentEngine, AgentConfig
        from gogoclaw.gateway.protocol import MessageRequest
        from gogoclaw.agent.model_client import MockClient
        
        config = AgentConfig(
            agent_id="main",
            name="GogoClaw",
            model_provider="mock",
            model_name="mock",
            system_prompt="You are helpful.",
            tools=[],
            sandbox_enabled=False,
            memory_enabled=False
        )
        
        engine = AgentEngine(config, temp_storage)
        engine.set_model_client(MockClient("Hello from mock"))
        
        request = MessageRequest(
            session_id="test-session",
            content="Hi there",
            channel="webui"
        )
        
        response = await engine.handle_message(request)
        
        assert response is not None
        assert response.role == "assistant"
        assert "Hello from mock" in response.content
        
    @pytest.mark.asyncio
    async def test_handle_message_creates_session(self, temp_storage):
        """测试消息处理创建会话"""
        from gogoclaw.agent.engine import AgentEngine, AgentConfig
        from gogoclaw.gateway.protocol import MessageRequest
        from gogoclaw.agent.model_client import MockClient
        
        config = AgentConfig(
            agent_id="main",
            name="GogoClaw",
            model_provider="mock",
            model_name="mock",
            system_prompt="Test",
            tools=[],
            sandbox_enabled=False,
            memory_enabled=False
        )
        
        engine = AgentEngine(config, temp_storage)
        engine.set_model_client(MockClient("Response"))
        
        request = MessageRequest(
            session_id="new-session-123",
            content="Hello",
            channel="telegram"
        )
        
        await engine.handle_message(request)
        
        # 检查会话已创建
        session = engine.session_manager.get_session("new-session-123")
        assert session is not None
        assert len(session.history) >= 2  # 用户消息 + 助手消息
