"""
GogoClaw 网关模块 - 访问控制
"""
from typing import Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Device:
    """已配对设备"""
    device_id: str
    device_key: str
    is_local: bool = False
    is_approved: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)


class AccessControl:
    """访问控制"""
    
    def __init__(self):
        self._devices: dict[str, Device] = {}
        self._whitelist: Set[str] = set()
        self._dm_policy = "pairing"  # pairing, open, deny
        self._group_policy = "mentioned"  # mentioned, always, deny
        self._group_whitelist: Set[str] = set()
        
    def set_policy(self, dm_policy: str = None, group_policy: str = None):
        """设置策略"""
        if dm_policy:
            self._dm_policy = dm_policy
        if group_policy:
            self._group_policy = group_policy
            
    def add_whitelist(self, identifier: str):
        """添加到白名单"""
        self._whitelist.add(identifier)
        
    def remove_whitelist(self, identifier: str):
        """从白名单移除"""
        self._whitelist.discard(identifier)
        
    def is_whitelisted(self, identifier: str) -> bool:
        """检查是否在白名单"""
        return identifier in self._whitelist
    
    def register_device(self, device_id: str, device_key: str, is_local: bool = False) -> Device:
        """注册设备"""
        device = Device(
            device_id=device_id,
            device_key=device_key,
            is_local=is_local,
            is_approved=is_local  # 本地设备自动通过
        )
        self._devices[device_id] = device
        return device
        
    def approve_device(self, device_id: str) -> bool:
        """审批设备"""
        if device_id in self._devices:
            self._devices[device_id].is_approved = True
            return True
        return False
        
    def is_device_approved(self, device_id: str) -> bool:
        """检查设备是否已审批"""
        device = self._devices.get(device_id)
        if not device:
            return False
        return device.is_local or device.is_approved
        
    def check_access(
        self, 
        channel: str, 
        sender: str, 
        is_group: bool = False,
        is_mentioned: bool = False
    ) -> tuple[bool, str]:
        """
        检查访问权限
        
        返回: (允许访问, 原因)
        """
        # 检查白名单
        if self.is_whitelisted(sender):
            return True, "whitelist"
            
        # 私聊策略
        if not is_group:
            if self._dm_policy == "open":
                return True, "dm_open"
            elif self._dm_policy == "deny":
                return False, "dm_deny"
            # pairing: 需要配对
            return False, "dm_pairing"
            
        # 群聊策略
        if self._group_policy == "always":
            return True, "group_always"
        elif self._group_policy == "deny":
            return False, "group_deny"
        # mentioned: 只在 @ 提到时响应
        elif self._group_policy == "mentioned":
            if is_mentioned:
                return True, "group_mentioned"
            return False, "group_not_mentioned"
            
        return False, "unknown"
        
    def add_group_whitelist(self, group_id: str):
        """添加群白名单"""
        self._group_whitelist.add(group_id)
        
    def is_group_whitelisted(self, group_id: str) -> bool:
        """检查群是否在白名单"""
        return group_id in self._group_whitelist
