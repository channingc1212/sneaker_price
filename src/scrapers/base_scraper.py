from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup

from ..utils.retry import with_retry, RateLimiter
from ..utils.config import config

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
        
    @abstractmethod
    async def search_product(self, query: str, **kwargs) -> List[SneakerProduct]:
        """Search for a product on the website."""
        pass
    
    @abstractmethod
    async def get_product_details(self, url: str) -> SneakerProduct:
        """Get detailed information about a specific product."""
        pass
    
    def _init_session(self):
        """Initialize a new session for requests."""
        import requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    @with_retry(max_retries=3, retry_delay=2)
    async def _make_request(self, url: str) -> str:
        """Make an HTTP request with error handling and retries."""
        if not self.session:
            self._init_session()
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"Failed to fetch {url}: {str(e)}")
    
    def clean_price(self, price_str: str) -> float:
        """Convert price string to float."""
        import re
        price = re.sub(r'[^\d.]', '', price_str)
        return float(price) if price else 0.0 