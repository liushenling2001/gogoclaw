"""
GogoClaw 智能体模块 - 会话管理
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict
import logging

from gogoclaw.gateway.protocol import Message

logger = logging.getLogger(__name__)


@dataclass
class Session:
    """会话"""
    session_id: str
    agent_id: str
    channel: str
    trust_level: str  # main, dm, group
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    history: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: Message):
        """添加消息"""
        self.history.append(message)
        self.last_active = datetime.now()
        
    def get_history_text(self, max_tokens: int = 8000) -> str:
        """获取历史文本 (用于上下文)"""
        # 简单估算: 1 token ≈ 4 字符
        max_chars = max_tokens * 4
        
        texts = []
        total_chars = 0
        
        # 从最近的消息开始
        for msg in reversed(self.history):
            msg_text = f"{msg.role}: {msg.content}\n"
            if total_chars + len(msg_text) > max_chars:
                break
            texts.insert(0, msg_text)
            total_chars += len(msg_text)
            
        return "".join(texts)
        
    def compact(self, summary: str):
        """压缩会话历史"""
        # 保留系统消息，第一条之后的消息压缩为摘要
        if len(self.history) > 2:
            # 保留前两条消息
            self.history = self.history[:2]
            # 添加摘要消息
            self.history.append(Message(
                session_id=self.session_id,
                role="system",
                content=f"[对话已压缩] {summary}"
            ))
            
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "channel": self.channel,
            "trust_level": self.trust_level,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "history": [m.model_dump(mode="json") for m in self.history],
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """从字典创建"""
        history = [Message(**m) for m in data.get("history", [])]
        return cls(
            session_id=data["session_id"],
            agent_id=data["agent_id"],
            channel=data["channel"],
            trust_level=data["trust_level"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_active=datetime.fromisoformat(data["last_active"]),
            history=history,
            metadata=data.get("metadata", {})
        )


class SessionManager:
    """会话管理器"""
    
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.sessions_dir = storage_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # 内存缓存
        self._cache: Dict[str, Session] = {}
        
    def _get_session_file(self, session_id: str) -> Path:
        """获取会话文件路径"""
        # 安全的文件名
        safe_id = session_id.replace(":", "_").replace("/", "_")
        return self.sessions_dir / f"{safe_id}.json"
        
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        # 尝试从缓存
        if session_id in self._cache:
            return self._cache[session_id]
            
        # 从磁盘加载
        session_file = self._get_session_file(session_id)
        if session_file.exists():
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                session = Session.from_dict(data)
                self._cache[session_id] = session
                return session
            except Exception as e:
                logger.error(f"Error loading session {session_id}: {e}")
                
        return None
        
    def create_session(
        self, 
        session_id: str, 
        agent_id: str = "main",
        channel: str = "webui",
        trust_level: str = "dm"
    ) -> Session:
        """创建新会话"""
        session = Session(
            session_id=session_id,
            agent_id=agent_id,
            channel=channel,
            trust_level=trust_level
        )
        
        self._cache[session_id] = session
        self._save_session(session)
        
        return session
        
    def save_session(self, session: Session):
        """保存会话"""
        self._save_session(session)
        
    def _save_session(self, session: Session):
        """保存会话到磁盘"""
        session_file = self._get_session_file(session.session_id)
        
        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving session {session.session_id}: {e}")
            
    def delete_session(self, session_id: str):
        """删除会话"""
        self._cache.pop(session_id, None)
        
        session_file = self._get_session_file(session_id)
        if session_file.exists():
            session_file.unlink()
            
    def list_sessions(self, agent_id: Optional[str] = None) -> List[Session]:
        """列出所有会话"""
        sessions = []
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                session = Session.from_dict(data)
                
                if agent_id is None or session.agent_id == agent_id:
                    sessions.append(session)
            except Exception as e:
                logger.error(f"Error loading session {session_file}: {e}")
                
        return sorted(sessions, key=lambda s: s.last_active, reverse=True)
        
    def cleanup_old_sessions(self, max_age_days: int = 30):
        """清理旧会话"""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=max_age_days)
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                if datetime.fromtimestamp(session_file.stat().st_mtime) < cutoff:
                    session_file.unlink()
                    logger.info(f"Deleted old session: {session_file.name}")
            except Exception as e:
                logger.error(f"Error cleaning session {session_file}: {e}")
