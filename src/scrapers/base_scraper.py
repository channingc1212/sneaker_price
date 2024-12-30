from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
import time
import aiohttp
import asyncio
from urllib.parse import urljoin

from ..utils.retry import with_retry, RateLimiter
from ..utils.config import config
from ..utils.proxy_manager import ProxyManager

logger = logging.getLogger(__name__)

@dataclass
class SneakerProduct:
    """Data class to store sneaker information."""
    name: str
    price: float
    url: str
    size: Optional[str] = None
    color: Optional[str] = None
    store: Optional[str] = None
    availability: bool = True
    image_url: Optional[str] = None

class BaseScraper(ABC):
    """Base class for all sneaker website scrapers."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.rate_limiter = RateLimiter(
            calls_per_minute=config.rate_limits.get(self.__class__.__name__, 60)
        )
        self.proxy_manager = ProxyManager()
        
    @abstractmethod
    async def search_product(self, query: str, **kwargs) -> List[SneakerProduct]:
        """Search for a product on the website."""
        pass
    
    @abstractmethod
    async def get_product_details(self, url: str) -> SneakerProduct:
        """Get detailed information about a specific product."""
        pass
    
    async def _init_session(self):
        """Initialize a new session for requests."""
        if not self.session or self.session.closed:
            self.session = await self.proxy_manager.get_session(self.base_url)
    
    async def _close_session(self):
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
        await self.proxy_manager.close_all_sessions()
    
    @with_retry()
    async def _make_request(self, url: str) -> str:
        """Make an HTTP request with error handling and retries."""
        if not self.session or self.session.closed:
            await self._init_session()
        
        try:
            # Clean URL to avoid bot detection
            clean_url = self.proxy_manager.clean_url(url)
            return await self.proxy_manager.make_request(clean_url, self.session)
                
        except aiohttp.ClientError as e:
            logger.error(f"Request error for {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {str(e)}")
            raise
    
    def clean_price(self, price_str: str) -> float:
        """Convert price string to float."""
        try:
            import re
            # Remove currency symbols and other non-numeric characters except decimal point
            price = re.sub(r'[^\d.]', '', price_str)
            return float(price) if price else 0.0
        except Exception as e:
            logger.error(f"Error cleaning price '{price_str}': {str(e)}")
            return 0.0
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._init_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_session() 