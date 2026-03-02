"""
GogoClaw 工具函数 - Web 页面抓取
"""
import httpx
import logging
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def fetch_url(
    url: str,
    timeout: int = 30,
    max_chars: int = 50000
) -> Dict[str, Any]:
    """
    抓取网页内容并提取可读文本
    
    Args:
        url: 要抓取的 URL
        timeout: 超时时间 (秒)
        max_chars: 最大返回字符数
        
    Returns:
        Dict with keys: url, title, content, success, error
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            html = response.text
            
            # 解析 HTML
            soup = BeautifulSoup(html, "html.parser")
            
            # 提取标题
            title = ""
            if soup.title:
                title = soup.title.string or ""
            
            # 移除不需要的元素
            for element in soup(["script", "style", "noscript", "iframe", "nav", "footer", "header"]):
                element.decompose()
            
            # 提取正文内容
            # 优先查找 main 标签
            main = soup.find("main") or soup.find("article") or soup.body
            
            if main:
                # 提取文本
                text = main.get_text(separator="\n", strip=True)
            else:
                text = soup.get_text(separator="\n", strip=True)
            
            # 限制长度
            if len(text) > max_chars:
                text = text[:max_chars] + "\n\n... (content truncated)"
            
            return {
                "url": url,
                "title": title,
                "content": text,
                "success": True
            }
            
    except httpx.TimeoutException as e:
        logger.error(f"URL fetch timeout: {url}")
        return {
            "url": url,
            "error": f"Request timeout after {timeout}s",
            "success": False
        }
    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {url} - {e}")
        return {
            "url": url,
            "error": f"HTTP error: {str(e)}",
            "success": False
        }
    except Exception as e:
        logger.error(f"URL fetch error: {url} - {e}")
        return {
            "url": url,
            "error": f"Error: {str(e)}",
            "success": False
        }
