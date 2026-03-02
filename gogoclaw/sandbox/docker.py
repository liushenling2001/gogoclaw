"""
GogoClaw 沙箱模块 - Docker 沙箱执行
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
import uuid

logger = logging.getLogger(__name__)


@dataclass
class SandboxConfig:
    """沙箱配置"""
    image: str = "gogoclaw/sandbox:latest"
    memory_limit: str = "512m"
    cpu_limit: float = 1.0
    network_disabled: bool = True
    working_dir: str = "/app"
    timeout: int = 30
    
    # 挂载卷
    volumes: Optional[Dict[str, str]] = None
    
    # 环境变量
    env: Optional[List[str]] = None


class DockerSandbox:
    """Docker 沙箱"""
    
    def __init__(self, config: SandboxConfig = None):
        self.config = config or SandboxConfig()
        self._client = None
        self._containers: Dict[str, Any] = {}
        
    async def start(self):
        """初始化 Docker 客户端"""
        try:
            import docker
            self._client = docker.from_env()
            # 测试连接
            self._client.ping()
            logger.info("Docker sandbox initialized")
        except ImportError:
            logger.warning("Docker SDK not installed, using fallback execution")
            self._client = None
        except Exception as e:
            logger.warning(f"Failed to connect to Docker: {e}")
            self._client = None
            
    async def stop(self):
        """停止所有容器"""
        if self._client:
            for container in self._containers.values():
                try:
                    container.stop(timeout=5)
                    container.remove()
                except Exception as e:
                    logger.error(f"Error stopping container: {e}")
        self._containers.clear()
        
    async def execute(
        self,
        command: str,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        在沙箱中执行命令
        
        Args:
            command: 要执行的命令
            env: 环境变量
            timeout: 超时时间(秒)
            session_id: 会话ID (用于隔离)
            
        Returns:
            执行结果 {"output": "...", "exit_code": 0, "error": None}
        """
        timeout = timeout or self.config.timeout
        
        # 如果 Docker 不可用，使用 fallback
        if not self._client:
            return await self._execute_fallback(command, timeout)
            
        # 创建唯一容器名
        container_name = f"gogoclaw_{session_id or uuid.uuid4().hex[:8]}"
        
        try:
            # 拉取镜像 (如果不存在)
            try:
                self._client.images.get(self.config.image)
            except:
                logger.info(f"Pulling image {self.config.image}...")
                self._client.images.pull(self.config.image)
                
            # 创建并启动容器
            container = self._client.containers.run(
                self.config.image,
                command=f"sh -c '{command}'",
                name=container_name,
                detach=True,
                mem_limit=self.config.memory_limit,
                cpu_period=100000,
                cpu_quota=int(self.config.cpu_limit * 100000),
                network_disabled=self.config.network_disabled,
                working_dir=self.config.working_dir,
                volumes=self.config.volumes or {},
                environment=env or {}
            )
            
            self._containers[container_name] = container
            
            # 等待执行完成
            result = container.wait(timeout=timeout)
            exit_code = result.get("StatusCode", 1)
            
            # 获取输出
            logs = container.logs(stdout=True, stderr=True).decode("utf-8")
            
            # 清理容器
            container.remove(force=True)
            self._containers.pop(container_name, None)
            
            return {
                "output": logs,
                "exit_code": exit_code,
                "error": None if exit_code == 0 else f"Exit code: {exit_code}"
            }
            
        except asyncio.TimeoutError:
            # 超时，终止容器
            if container_name in self._containers:
                self._containers[container_name].stop(timeout=5)
                self._containers[container_name].remove()
            return {
                "output": "",
                "exit_code": -1,
                "error": "Command timeout"
            }
        except Exception as e:
            logger.error(f"Sandbox execution error: {e}")
            return {
                "output": "",
                "exit_code": -1,
                "error": str(e)
            }
            
    async def _execute_fallback(
        self, 
        command: str, 
        timeout: int
    ) -> Dict[str, Any]:
        """Fallback 执行 (不使用 Docker)"""
        # 限制可执行的命令
        allowed_commands = ["echo", "pwd", "ls", "cat", "head", "tail", "wc", "grep"]
        
        # 简单检查
        first_word = command.strip().split()[0] if command.strip() else ""
        if first_word not in allowed_commands:
            return {
                "output": "",
                "exit_code": 1,
                "error": f"Command not allowed in sandbox: {first_word}"
            }
            
        # 使用 asyncio 子进程
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                output = stdout.decode("utf-8")
                error = stderr.decode("utf-8")
                
                return {
                    "output": output,
                    "exit_code": process.returncode or 0,
                    "error": error if process.returncode != 0 else None
                }
                
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "output": "",
                    "exit_code": -1,
                    "error": "Command timeout"
                }
                
        except Exception as e:
            return {
                "output": "",
                "exit_code": -1,
                "error": str(e)
            }
            
    async def execute_file_operation(
        self,
        operation: str,  # read, write, list
        path: str,
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """文件操作"""
        if operation == "read":
            command = f"cat {path}"
        elif operation == "write":
            command = f"echo '{content}' > {path}"
        elif operation == "list":
            command = f"ls -la {path}"
        else:
            return {"error": f"Unknown operation: {operation}"}
            
        return await self.execute(command)


class SandboxManager:
    """沙箱管理器"""
    
    def __init__(self, config: SandboxConfig = None):
        self.config = config or SandboxConfig()
        self._sandboxes: Dict[str, DockerSandbox] = {}
        
    async def get_sandbox(self, session_id: str) -> DockerSandbox:
        """获取会话的沙箱"""
        if session_id not in self._sandboxes:
            # 创建新沙箱
            self._sandboxes[session_id] = DockerSandbox(self.config)
            await self._sandboxes[session_id].start()
        return self._sandboxes[session_id]
        
    async def release_sandbox(self, session_id: str):
        """释放沙箱"""
        if session_id in self._sandboxes:
            await self._sandboxes[session_id].stop()
            del self._sandboxes[session_id]
            
    async def shutdown(self):
        """关闭所有沙箱"""
        for sandbox in self._sandboxes.values():
            await sandbox.stop()
        self._sandboxes.clear()
