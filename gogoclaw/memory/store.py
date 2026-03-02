"""
GogoClaw 记忆模块 - 存储
"""
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import logging
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class MemoryItem:
    """记忆项"""
    id: str
    session_id: str
    role: str  # user, assistant, system
    content: str
    embedding: Optional[List[float]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class MemoryStore:
    """记忆存储"""
    
    def __init__(
        self, 
        storage_dir: Path,
        vector_enabled: bool = True,
        embedding_model: str = "text-embedding-3-small"
    ):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.vector_enabled = vector_enabled
        self.embedding_model = embedding_model
        
        # SQLite 数据库
        self.db_path = storage_dir / "memory.db"
        self._init_db()
        
        # 向量存储 (可选)
        self._vector_store = None
        if vector_enabled:
            self._init_vector_store()
            
    def _init_db(self):
        """初始化 SQLite 数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 记忆表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                indexed BOOLEAN DEFAULT 0
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session 
            ON memories(session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created 
            ON memories(created_at)
        """)
        
        conn.commit()
        conn.close()
        
    def _init_vector_store(self):
        """初始化向量存储"""
        # 尝试导入向量数据库客户端
        try:
            # 优先使用 qdrant
            from qdrant_client import QdrantClient
            self._vector_store = QdrantClient(path=str(self.storage_dir / "vectors"))
            self._vector_store.recreate_collection(
                collection_name="memories",
                vectors_config={"size": 1536, "distance": "Cosine"}
            )
            logger.info("Initialized Qdrant vector store")
        except ImportError:
            try:
                # 备选: chroma
                import chromadb
                self._vector_store = chromadb.PersistentClient(
                    path=str(self.storage_dir / "vectors")
                )
                # 获取或创建 collection
                self._chroma_collection = self._vector_store.get_or_create_collection(
                    name="memories",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("Initialized Chroma vector store")
            except ImportError:
                logger.warning("No vector store available, using SQLite only")
                self.vector_enabled = False
                
    async def add(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """添加记忆"""
        # 生成 ID
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        memory_id = f"{session_id}_{role}_{content_hash}_{int(datetime.now().timestamp())}"
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO memories (id, session_id, role, content) VALUES (?, ?, ?, ?)",
            (memory_id, session_id, role, content)
        )
        
        conn.commit()
        conn.close()
        
        # 添加到向量存储
        if self.vector_enabled and self._vector_store:
            await self._add_to_vector(memory_id, content)
            
        return memory_id
        
    async def _add_to_vector(self, memory_id: str, content: str):
        """添加到向量存储"""
        try:
            # 获取 embedding
            embedding = await self._get_embedding(content)
            if not embedding:
                return
                
            # 存储到向量数据库
            try:
                self._vector_store.upsert(
                    collection_name="memories",
                    points=[{
                        "id": memory_id,
                        "vector": embedding,
                        "payload": {"content": content}
                    }]
                )
            except AttributeError:
                # Chroma
                self._chroma_collection.upsert(
                    ids=[memory_id],
                    embeddings=[embedding],
                    documents=[content]
                )
                
        except Exception as e:
            logger.error(f"Error adding to vector store: {e}")
            
    async def _get_embedding(self, text: str) -> Optional[List[float]]:
        """获取文本的 embedding"""
        # TODO: 实现真正的 embedding 调用
        # 这里使用简单的模拟
        # 实际应该调用 OpenAI/HuggingFace 等 embedding API
        return None
        
    async def search(
        self, 
        query: str, 
        limit: int = 5,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """搜索记忆"""
        results = []
        
        # 1. 向量搜索
        if self.vector_enabled and self._vector_store:
            try:
                vector_results = await self._vector_search(query, limit)
                results.extend(vector_results)
            except Exception as e:
                logger.warning(f"Vector search error: {e}")
                
        # 2. 关键词搜索 (BM25 简化版)
        if len(results) < limit:
            keyword_results = await self._keyword_search(query, limit - len(results), session_id)
            results.extend(keyword_results)
            
        # 去重并返回
        seen = set()
        unique_results = []
        for r in results:
            if r["id"] not in seen:
                seen.add(r["id"])
                unique_results.append(r)
                
        return unique_results[:limit]
        
    async def _vector_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """向量搜索"""
        # 获取 query 的 embedding
        query_embedding = await self._get_embedding(query)
        if not query_embedding:
            return []
            
        try:
            # Qdrant
            results = self._vector_store.search(
                collection_name="memories",
                query_vector=query_embedding,
                limit=limit
            )
            return [{"id": r.id, "content": r.payload["content"], "score": r.score} for r in results]
        except AttributeError:
            # Chroma
            results = self._chroma_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            return [
                {"id": id, "content": doc, "score": 1.0 - dist}
                for id, doc, dist in zip(
                    results["ids"][0], 
                    results["documents"][0],
                    results["distances"][0]
                )
            ]
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []
            
    async def _keyword_search(
        self, 
        query: str, 
        limit: int,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """关键词搜索 (SQL LIKE)"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 简单的 LIKE 搜索
        search_pattern = f"%{query}%"
        
        if session_id:
            cursor.execute(
                """SELECT id, session_id, role, content, created_at 
                   FROM memories 
                   WHERE session_id = ? AND content LIKE ?
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (session_id, search_pattern, limit)
            )
        else:
            cursor.execute(
                """SELECT id, session_id, role, content, created_at 
                   FROM memories 
                   WHERE content LIKE ?
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (search_pattern, limit)
            )
            
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "session_id": row[1],
                "role": row[2],
                "content": row[3],
                "created_at": row[4],
                "score": 0.5  # 默认分数
            }
            for row in rows
        ]
        
    async def get_session_history(
        self, 
        session_id: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取会话历史"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, role, content, created_at 
               FROM memories 
               WHERE session_id = ?
               ORDER BY created_at DESC
               LIMIT ?""",
            (session_id, limit)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "role": row[1],
                "content": row[2],
                "created_at": row[3]
            }
            for row in rows
        ]
        
    async def delete_session(self, session_id: str):
        """删除会话记忆"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM memories WHERE session_id = ?", (session_id,))
        
        conn.commit()
        conn.close()
        
        # TODO: 从向量存储中删除
        
    def close(self):
        """关闭连接"""
        if self._vector_store:
            # Qdrant 没有 close 方法
            pass
