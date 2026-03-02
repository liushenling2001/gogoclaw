"""
GogoClaw 配置管理测试
测试配置加载、环境变量和配置文件处理
"""
import pytest
import os
import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestChannelConfig:
    """渠道配置测试"""
    
    def test_channel_config_creation(self):
        """测试渠道配置创建"""
        from gogoclaw.config.settings import ChannelConfig
        
        config = ChannelConfig(
            enabled=True,
            whitelist=["user1", "user2"],
            dm_policy="open",
            group_policy="always",
            group_whitelist=["group1"]
        )
        
        assert config.enabled is True
        assert "user1" in config.whitelist
        assert config.dm_policy == "open"
        assert config.group_policy == "always"
        assert "group1" in config.group_whitelist
        
    def test_channel_config_defaults(self):
        """测试渠道配置默认值"""
        from gogoclaw.config.settings import ChannelConfig
        
        config = ChannelConfig()
        
        assert config.enabled is True
        assert config.whitelist == []
        assert config.dm_policy == "pairing"
        assert config.group_policy == "mentioned"
        assert config.group_whitelist == []


class TestModelConfig:
    """模型配置测试"""
    
    def test_model_config_creation(self):
        """测试模型配置创建"""
        from gogoclaw.config.settings import ModelConfig
        
        config = ModelConfig(
            provider="openai",
            model_name="gpt-4o",
            api_key="sk-test123",
            temperature=0.7,
            max_tokens=4096
        )
        
        assert config.provider == "openai"
        assert config.model_name == "gpt-4o"
        assert config.api_key == "sk-test123"
        assert config.temperature == 0.7
        assert config.max_tokens == 4096
        
    def test_model_config_defaults(self):
        """测试模型配置默认值"""
        from gogoclaw.config.settings import ModelConfig
        
        config = ModelConfig()
        
        assert config.provider == "openai"
        assert config.model_name == "gpt-4o"
        assert config.api_key is None
        assert config.temperature == 0.7
        assert config.max_tokens == 4096


class TestAgentConfig:
    """智能体配置测试"""
    
    def test_agent_config_creation(self):
        """测试智能体配置创建"""
        from gogoclaw.config.settings import AgentConfig, ModelConfig
        
        model_config = ModelConfig(provider="anthropic", model_name="claude-3-5-sonnet")
        
        config = AgentConfig(
            agent_id="main",
            name="GogoClaw",
            model=model_config,
            tools=["command", "browser", "file"],
            system_prompt="You are helpful.",
            sandbox_enabled=True,
            memory_enabled=True
        )
        
        assert config.agent_id == "main"
        assert config.name == "GogoClaw"
        assert config.model.provider == "anthropic"
        assert "command" in config.tools
        assert config.sandbox_enabled is True
        
    def test_agent_config_defaults(self):
        """测试智能体配置默认值"""
        from gogoclaw.config.settings import AgentConfig
        
        config = AgentConfig()
        
        assert config.agent_id == "main"
        assert config.name == "GogoClaw"
        assert config.model.provider == "openai"
        assert config.sandbox_enabled is True
        assert config.memory_enabled is True


class TestGatewayConfig:
    """网关配置测试"""
    
    def test_gateway_config_creation(self):
        """测试网关配置创建"""
        from gogoclaw.config.settings import GatewayConfig
        
        config = GatewayConfig(
            host="0.0.0.0",
            port=8080,
            auth_enabled=True,
            cors_origins=["http://localhost:3000"]
        )
        
        assert config.host == "0.0.0.0"
        assert config.port == 8080
        assert config.auth_enabled is True
        assert "http://localhost:3000" in config.cors_origins
        
    def test_gateway_config_defaults(self):
        """测试网关配置默认值"""
        from gogoclaw.config.settings import GatewayConfig
        
        config = GatewayConfig()
        
        assert config.host == "127.0.0.1"
        assert config.port == 18789
        assert config.auth_enabled is False
        assert "*" in config.cors_origins


class TestMemoryConfig:
    """记忆配置测试"""
    
    def test_memory_config_creation(self):
        """测试记忆配置创建"""
        from gogoclaw.config.settings import MemoryConfig
        
        config = MemoryConfig(
            provider="qdrant",
            vector_enabled=True,
            embedding_model="text-embedding-3-small",
            similarity_top_k=10
        )
        
        assert config.provider == "qdrant"
        assert config.vector_enabled is True
        assert config.embedding_model == "text-embedding-3-small"
        assert config.similarity_top_k == 10
        
    def test_memory_config_defaults(self):
        """测试记忆配置默认值"""
        from gogoclaw.config.settings import MemoryConfig
        
        config = MemoryConfig()
        
        assert config.provider == "sqlite"
        assert config.vector_enabled is True
        assert config.similarity_top_k == 5


class TestSettings:
    """全局设置测试"""
    
    def test_settings_creation(self):
        """测试全局设置创建"""
        from gogoclaw.config.settings import Settings
        
        settings = Settings()
        
        assert settings.gateway is not None
        assert settings.agents is not None
        assert "main" in settings.agents
        assert settings.memory is not None
        
    def test_settings_gateway_access(self):
        """测试网关配置访问"""
        from gogoclaw.config.settings import Settings
        
        settings = Settings()
        
        assert settings.gateway.host == "127.0.0.1"
        assert settings.gateway.port == 18789
        
    def test_settings_agents_access(self):
        """测试智能体配置访问"""
        from gogoclaw.config.settings import Settings
        
        settings = Settings()
        
        main_agent = settings.agents["main"]
        assert main_agent.agent_id == "main"
        assert main_agent.name == "GogoClaw"
        
    def test_settings_singleton(self):
        """测试设置单例模式"""
        from gogoclaw.config.settings import get_settings
        
        s1 = get_settings()
        s2 = get_settings()
        
        assert s1 is s2


class TestEnvVariableLoading:
    """环境变量加载测试"""
    
    def test_load_from_env_prefix(self):
        """测试带前缀的环境变量加载"""
        import os
        from gogoclaw.config.settings import Settings, init_settings
        
        # 保存原值
        original_debug = os.environ.get("GOGOCLAW_DEBUG")
        
        try:
            os.environ["GOGOCLAW_DEBUG"] = "true"
            
            # 重新初始化
            settings = init_settings()
            
            assert settings.debug is True
        finally:
            if original_debug:
                os.environ["GOGOCLAW_DEBUG"] = original_debug
            elif "GOGOCLAW_DEBUG" in os.environ:
                del os.environ["GOGOCLAW_DEBUG"]
                
    def test_load_nested_env(self):
        """测试嵌套环境变量加载"""
        import os
        from gogoclaw.config.settings import Settings, init_settings
        
        # 保存原值
        original_provider = os.environ.get("GOGOCLAW_AGENTS__MAIN__MODEL__PROVIDER")
        original_model = os.environ.get("GOGOCLAW_AGENTS__MAIN__MODEL__MODEL_NAME")
        
        try:
            os.environ["GOGOCLAW_AGENTS__MAIN__MODEL__PROVIDER"] = "anthropic"
            os.environ["GOGOCLAW_AGENTS__MAIN__MODEL__MODEL_NAME"] = "claude-3-5-sonnet"
            
            settings = init_settings()
            
            assert settings.agents["main"].model.provider == "anthropic"
            assert settings.agents["main"].model.model_name == "claude-3-5-sonnet"
        finally:
            if original_provider:
                os.environ["GOGOCLAW_AGENTS__MAIN__MODEL__PROVIDER"] = original_provider
            elif "GOGOCLAW_AGENTS__MAIN__MODEL__PROVIDER" in os.environ:
                del os.environ["GOGOCLAW_AGENTS__MAIN__MODEL__PROVIDER"]
                
            if original_model:
                os.environ["GOGOCLAW_AGENTS__MAIN__MODEL__MODEL_NAME"] = original_model
            elif "GOGOCLAW_AGENTS__MAIN__MODEL__MODEL_NAME" in os.environ:
                del os.environ["GOGOCLAW_AGENTS__MAIN__MODEL__MODEL_NAME"]


class TestConfigFileLoading:
    """配置文件加载测试"""
    
    def test_load_from_json_file(self):
        """测试从 JSON 文件加载配置"""
        from gogoclaw.config.settings import Settings
        import json
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "gogoclaw.json"
            
            config_data = {
                "gateway": {
                    "host": "0.0.0.0",
                    "port": 9000
                },
                "agents": {
                    "main": {
                        "model": {
                            "provider": "openai",
                            "model_name": "gpt-4o-mini"
                        }
                    }
                }
            }
            
            config_file.write_text(json.dumps(config_data))
            
            settings = Settings()
            settings.load_from_file(config_file)
            
            assert settings.gateway.host == "0.0.0.0"
            assert settings.gateway.port == 9000
            assert settings.agents["main"].model.model_name == "gpt-4o-mini"
            
    def test_load_from_json5_with_comments(self):
        """测试从带注释的 JSON5 文件加载"""
        from gogoclaw.config.settings import Settings
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json5"
            
            # JSON5 格式（带注释和尾随逗号）
            config_content = """
            {
                // 网关配置
                "gateway": {
                    "host": "127.0.0.1",
                    "port": 18789,
                },
                /* 智能体配置 */
                "agents": {
                    "main": {
                        "name": "GogoClaw",
                    }
                }
            }
            """
            
            config_file.write_text(config_content)
            
            settings = Settings()
            settings.load_from_file(config_file)
            
            assert settings.gateway.port == 18789
            assert settings.agents["main"].name == "GogoClaw"
            
    def test_load_nonexistent_file(self):
        """测试加载不存在的配置文件"""
        from gogoclaw.config.settings import Settings
        
        settings = Settings()
        
        # 应该不抛出异常
        settings.load_from_file(Path("/nonexistent/config.json"))
        
    def test_init_settings(self):
        """测试初始化设置"""
        from gogoclaw.config.settings import init_settings
        
        settings = init_settings(debug=True)
        
        assert settings.debug is True


class TestErrorHandling:
    """错误处理测试"""
    
    def test_invalid_json_file(self):
        """测试无效 JSON 文件处理"""
        from gogoclaw.config.settings import Settings
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "invalid.json"
            config_file.write_text("not valid json {{{")
            
            settings = Settings()
            
            # 应该抛出异常
            import pytest
            with pytest.raises(json.JSONDecodeError):
                settings.load_from_file(config_file)
