"""
GogoClaw 渠道适配器测试
测试渠道适配器的接口和功能
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestChannelType:
    """渠道类型枚举测试"""
    
    def test_channel_type_values(self):
        """测试渠道类型值"""
        from gogoclaw.channels.base import ChannelType
        
        assert ChannelType.TELEGRAM.value == "telegram"
        assert ChannelType.DISCORD.value == "discord"
        assert ChannelType.WHATSAPP.value == "whatsapp"
        assert ChannelType.FEISHU.value == "feishu"
        assert ChannelType.DINGTALK.value == "dingtalk"
        assert ChannelType.WEBUI.value == "webui"


class TestChannelMessage:
    """渠道消息测试"""
    
    def test_channel_message_creation(self):
        """测试渠道消息创建"""
        from gogoclaw.channels.base import ChannelMessage
        
        msg = ChannelMessage(
            message_id="msg-123",
            channel="telegram",
            sender_id="user-456",
            sender_name="Test User",
            content="Hello, bot!"
        )
        
        assert msg.message_id == "msg-123"
        assert msg.channel == "telegram"
        assert msg.sender_id == "user-456"
        assert msg.sender_name == "Test User"
        assert msg.content == "Hello, bot!"
        assert msg.is_group is False
        assert msg.is_mentioned is False
        
    def test_channel_message_group(self):
        """测试群聊消息"""
        from gogoclaw.channels.base import ChannelMessage
        
        msg = ChannelMessage(
            message_id="msg-789",
            channel="telegram",
            sender_id="user-456",
            sender_name="Test User",
            content="@bot Hello!",
            is_group=True,
            group_id="group-123",
            is_mentioned=True
        )
        
        assert msg.is_group is True
        assert msg.group_id == "group-123"
        assert msg.is_mentioned is True
        
    def test_channel_message_platform_property(self):
        """测试平台名称属性"""
        from gogoclaw.channels.base import ChannelMessage
        
        msg = ChannelMessage(
            message_id="msg-1",
            channel="discord",
            sender_id="user-1",
            sender_name="User",
            content="Hi"
        )
        
        assert msg.platform == "discord"
        
    def test_channel_message_metadata(self):
        """测试消息元数据"""
        from gogoclaw.channels.base import ChannelMessage
        
        msg = ChannelMessage(
            message_id="msg-1",
            channel="feishu",
            sender_id="user-1",
            sender_name="User",
            content="Hi",
            metadata={"thread_id": "thread-123", "tenant_key": "tenant-456"}
        )
        
        assert msg.metadata["thread_id"] == "thread-123"
        assert msg.metadata["tenant_key"] == "tenant-456"


class TestChannelConfig:
    """渠道配置测试"""
    
    def test_channel_config_defaults(self):
        """测试渠道配置默认值"""
        from gogoclaw.channels.base import ChannelConfig
        
        config = ChannelConfig()
        
        assert config.enabled is True
        assert config.dm_policy == "pairing"
        assert config.group_policy == "mentioned"
        assert config.whitelist == []
        assert config.group_whitelist == []
        
    def test_channel_config_custom(self):
        """测试自定义渠道配置"""
        from gogoclaw.channels.base import ChannelConfig
        
        config = ChannelConfig(
            enabled=False,
            dm_policy="deny",
            group_policy="always",
            whitelist=["user1", "user2"],
            group_whitelist=["group1"]
        )
        
        assert config.enabled is False
        assert config.dm_policy == "deny"
        assert config.group_policy == "always"
        assert "user1" in config.whitelist
        assert "group1" in config.group_whitelist


class TestChannelAdapter:
    """渠道适配器基类测试"""
    
    def test_channel_adapter_init(self):
        """测试渠道适配器初始化"""
        from gogoclaw.channels.base import ChannelAdapter, ChannelType, ChannelConfig
        
        class TestAdapter(ChannelAdapter):
            async def start(self):
                pass
            async def stop(self):
                pass
            async def send_message(self, receiver_id, content, metadata=None):
                pass
            async def send_typing(self, receiver_id):
                pass
                
        config = ChannelConfig()
        adapter = TestAdapter(ChannelType.TELEGRAM, config)
        
        assert adapter.channel_type == ChannelType.TELEGRAM
        assert adapter.config == config
        assert adapter._message_handler is None
        
    def test_channel_adapter_set_message_handler(self):
        """测试设置消息处理器"""
        from gogoclaw.channels.base import ChannelAdapter, ChannelType, ChannelConfig
        
        class TestAdapter(ChannelAdapter):
            async def start(self):
                pass
            async def stop(self):
                pass
            async def send_message(self, receiver_id, content, metadata=None):
                pass
            async def send_typing(self, receiver_id):
                pass
                
        adapter = TestAdapter(ChannelType.TELEGRAM, ChannelConfig())
        
        async def handler(msg):
            pass
            
        adapter.set_message_handler(handler)
        
        assert adapter._message_handler is handler
        
    @pytest.mark.asyncio
    async def test_channel_adapter_handle_message(self):
        """测试处理消息"""
        from gogoclaw.channels.base import ChannelAdapter, ChannelType, ChannelConfig, ChannelMessage
        
        class TestAdapter(ChannelAdapter):
            async def start(self):
                pass
            async def stop(self):
                pass
            async def send_message(self, receiver_id, content, metadata=None):
                pass
            async def send_typing(self, receiver_id):
                pass
                
        adapter = TestAdapter(ChannelType.TELEGRAM, ChannelConfig())
        
        received_messages = []
        
        async def handler(msg):
            received_messages.append(msg)
            
        adapter.set_message_handler(handler)
        
        msg = ChannelMessage(
            message_id="msg-1",
            channel="telegram",
            sender_id="user-1",
            sender_name="User",
            content="Hello"
        )
        
        await adapter.handle_message(msg)
        
        assert len(received_messages) == 1
        assert received_messages[0].content == "Hello"
        
    def test_channel_adapter_check_access_whitelist(self):
        """测试访问检查 - 白名单"""
        from gogoclaw.channels.base import ChannelAdapter, ChannelType, ChannelConfig, ChannelMessage
        
        class TestAdapter(ChannelAdapter):
            async def start(self):
                pass
            async def stop(self):
                pass
            async def send_message(self, receiver_id, content, metadata=None):
                pass
            async def send_typing(self, receiver_id):
                pass
                
        config = ChannelConfig(whitelist=["admin1", "admin2"])
        adapter = TestAdapter(ChannelType.TELEGRAM, config)
        
        msg = ChannelMessage(
            message_id="msg-1",
            channel="telegram",
            sender_id="admin1",
            sender_name="Admin",
            content="Hi"
        )
        
        allowed, reason = adapter.check_access(msg)
        
        assert allowed is True
        assert reason == "whitelist"
        
    def test_channel_adapter_check_access_dm_open(self):
        """测试访问检查 - 私聊开放"""
        from gogoclaw.channels.base import ChannelAdapter, ChannelType, ChannelConfig, ChannelMessage
        
        class TestAdapter(ChannelAdapter):
            async def start(self):
                pass
            async def stop(self):
                pass
            async def send_message(self, receiver_id, content, metadata=None):
                pass
            async def send_typing(self, receiver_id):
                pass
                
        config = ChannelConfig(dm_policy="open")
        adapter = TestAdapter(ChannelType.TELEGRAM, config)
        
        msg = ChannelMessage(
            message_id="msg-1",
            channel="telegram",
            sender_id="user-1",
            sender_name="User",
            content="Hi",
            is_group=False
        )
        
        allowed, reason = adapter.check_access(msg)
        
        assert allowed is True
        assert reason == "dm_open"
        
    def test_channel_adapter_check_access_dm_deny(self):
        """测试访问检查 - 私聊拒绝"""
        from gogoclaw.channels.base import ChannelAdapter, ChannelType, ChannelConfig, ChannelMessage
        
        class TestAdapter(ChannelAdapter):
            async def start(self):
                pass
            async def stop(self):
                pass
            async def send_message(self, receiver_id, content, metadata=None):
                pass
            async def send_typing(self, receiver_id):
                pass
                
        config = ChannelConfig(dm_policy="deny")
        adapter = TestAdapter(ChannelType.TELEGRAM, config)
        
        msg = ChannelMessage(
            message_id="msg-1",
            channel="telegram",
            sender_id="user-1",
            sender_name="User",
            content="Hi",
            is_group=False
        )
        
        allowed, reason = adapter.check_access(msg)
        
        assert allowed is False
        assert reason == "dm_deny"
        
    def test_channel_adapter_check_access_group_mentioned(self):
        """测试访问检查 - 群聊提及"""
        from gogoclaw.channels.base import ChannelAdapter, ChannelType, ChannelConfig, ChannelMessage
        
        class TestAdapter(ChannelAdapter):
            async def start(self):
                pass
            async def stop(self):
                pass
            async def send_message(self, receiver_id, content, metadata=None):
                pass
            async def send_typing(self, receiver_id):
                pass
                
        config = ChannelConfig(group_policy="mentioned")
        adapter = TestAdapter(ChannelType.TELEGRAM, config)
        
        msg = ChannelMessage(
            message_id="msg-1",
            channel="telegram",
            sender_id="user-1",
            sender_name="User",
            content="@bot Hi!",
            is_group=True,
            is_mentioned=True
        )
        
        allowed, reason = adapter.check_access(msg)
        
        assert allowed is True
        assert reason == "group_mentioned"
        
    def test_channel_adapter_check_access_group_not_mentioned(self):
        """测试访问检查 - 群聊未提及"""
        from gogoclaw.channels.base import ChannelAdapter, ChannelType, ChannelConfig, ChannelMessage
        
        class TestAdapter(ChannelAdapter):
            async def start(self):
                pass
            async def stop(self):
                pass
            async def send_message(self, receiver_id, content, metadata=None):
                pass
            async def send_typing(self, receiver_id):
                pass
                
        config = ChannelConfig(group_policy="mentioned")
        adapter = TestAdapter(ChannelType.TELEGRAM, config)
        
        msg = ChannelMessage(
            message_id="msg-1",
            channel="telegram",
            sender_id="user-1",
            sender_name="User",
            content="Hi everyone!",
            is_group=True,
            is_mentioned=False
        )
        
        allowed, reason = adapter.check_access(msg)
        
        assert allowed is False
        assert reason == "group_not_mentioned"
        
    def test_channel_adapter_check_access_group_always(self):
        """测试访问检查 - 群聊总是允许"""
        from gogoclaw.channels.base import ChannelAdapter, ChannelType, ChannelConfig, ChannelMessage
        
        class TestAdapter(ChannelAdapter):
            async def start(self):
                pass
            async def stop(self):
                pass
            async def send_message(self, receiver_id, content, metadata=None):
                pass
            async def send_typing(self, receiver_id):
                pass
                
        config = ChannelConfig(group_policy="always")
        adapter = TestAdapter(ChannelType.TELEGRAM, config)
        
        msg = ChannelMessage(
            message_id="msg-1",
            channel="telegram",
            sender_id="user-1",
            sender_name="User",
            content="Hi!",
            is_group=True,
            is_mentioned=False
        )
        
        allowed, reason = adapter.check_access(msg)
        
        assert allowed is True
        assert reason == "group_always"


class TestWebUIAdapter:
    """WebUI 适配器测试"""
    
    @pytest.mark.asyncio
    async def test_webui_adapter_start(self):
        """测试 WebUI 适配器启动"""
        from gogoclaw.channels.base import WebUIAdapter, ChannelConfig
        
        adapter = WebUIAdapter()
        await adapter.start()
        
        # 应该不抛出异常
        assert adapter.channel_type.value == "webui"
        
    @pytest.mark.asyncio
    async def test_webui_adapter_stop(self):
        """测试 WebUI 适配器停止"""
        from gogoclaw.channels.base import WebUIAdapter
        
        adapter = WebUIAdapter()
        await adapter.stop()
        
        # 应该不抛出异常
        
    @pytest.mark.asyncio
    async def test_webui_adapter_send_message(self):
        """测试 WebUI 适配器发送消息"""
        from gogoclaw.channels.base import WebUIAdapter
        
        adapter = WebUIAdapter()
        await adapter.send_message("receiver-1", "Hello")
        
        # WebUI 适配器由 Gateway 处理，应该不抛出异常
        
    @pytest.mark.asyncio
    async def test_webui_adapter_send_typing(self):
        """测试 WebUI 适配器发送输入状态"""
        from gogoclaw.channels.base import WebUIAdapter
        
        adapter = WebUIAdapter()
        await adapter.send_typing("receiver-1")
        
        # 应该不抛出异常


class TestChannelImplementations:
    """渠道实现测试"""
    
    def test_telegram_adapter_exists(self):
        """测试 Telegram 适配器存在"""
        from gogoclaw.channels.telegram import TelegramAdapter
        
        # 检查类存在
        assert TelegramAdapter is not None
        
    def test_discord_adapter_exists(self):
        """测试 Discord 适配器存在"""
        from gogoclaw.channels.discord import DiscordAdapter
        
        assert DiscordAdapter is not None
        
    def test_feishu_adapter_exists(self):
        """测试飞书适配器存在"""
        from gogoclaw.channels.feishu import FeishuAdapter
        
        assert FeishuAdapter is not None
        
    def test_dingtalk_adapter_exists(self):
        """测试钉钉适配器存在"""
        from gogoclaw.channels.dingtalk import DingTalkAdapter
        
        assert DingTalkAdapter is not None
        
    def test_whatsapp_adapter_exists(self):
        """测试 WhatsApp 适配器存在"""
        from gogoclaw.channels.whatsapp import WhatsAppAdapter
        
        assert WhatsAppAdapter is not None
