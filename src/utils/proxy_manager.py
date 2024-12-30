import random
import logging
import asyncio
from typing import Optional, Dict, List
import aiohttp
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class ProxyManager:
    """Manages proxy rotation and browser-like headers."""
    
    def __init__(self):
        self.user_agent = UserAgent()
        self.current_proxy = None
        
        # Common browser headers
        self.common_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        # Store cookies per domain
        self.cookies: Dict[str, Dict] = {}
        
        # Store sessions per domain
        self.sessions: Dict[str, aiohttp.ClientSession] = {}
    
    def _get_random_headers(self, url: str) -> Dict[str, str]:
        """Generate random browser-like headers."""
        headers = self.common_headers.copy()
        headers['User-Agent'] = self.user_agent.random
        
        # Add referer for known domains
        domain = url.split('/')[2]
        if 'nike' in domain:
            headers['Referer'] = 'https://www.nike.com/'
        elif 'footlocker' in domain:
            headers['Referer'] = 'https://www.footlocker.com/'
        elif 'finishline' in domain:
            headers['Referer'] = 'https://www.finishline.com/'
        elif 'dickssportinggoods' in domain:
            headers['Referer'] = 'https://www.dickssportinggoods.com/'
            
        return headers
    
    async def get_session(self, url: str) -> aiohttp.ClientSession:
        """Get an aiohttp session with appropriate headers and cookies."""
        domain = url.split('/')[2]
        
        # Return existing session if available
        if domain in self.sessions and not self.sessions[domain].closed:
            return self.sessions[domain]
        
        # Create new session
        headers = self._get_random_headers(url)
        session = aiohttp.ClientSession(
            headers=headers,
            cookie_jar=aiohttp.CookieJar(unsafe=True)
        )
        
        # Load existing cookies
        if domain in self.cookies:
            for name, value in self.cookies[domain].items():
                session.cookie_jar.update_cookies({name: value}, response_url=url)
        
        # Store session
        self.sessions[domain] = session
        return session
    
    async def make_request(self, url: str, session: Optional[aiohttp.ClientSession] = None) -> str:
        """Make a request with anti-bot measures."""
        own_session = False
        try:
            if not session:
                session = await self.get_session(url)
                own_session = True
            
            # Add random delay between requests (0.5 to 2 seconds)
            await asyncio.sleep(random.uniform(0.5, 2))
            
            async with session.get(url) as response:
                # Store cookies for future requests
                domain = url.split('/')[2]
                self.cookies[domain] = {
                    cookie.key: cookie.value 
                    for cookie in session.cookie_jar
                }
                
                # Check response
                if response.status == 403:
                    logger.warning(f"Access forbidden for {url}. Might need to implement additional anti-bot measures.")
                elif response.status == 404:
                    logger.warning(f"Page not found for {url}. The URL might be incorrect.")
                
                response.raise_for_status()
                return await response.text()
                
        except Exception as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            raise
        finally:
            if own_session and session and not session.closed:
                await session.close()
    
    async def close_all_sessions(self):
        """Close all active sessions."""
        for session in self.sessions.values():
            if not session.closed:
                await session.close()
        self.sessions.clear()
    
    @staticmethod
    def clean_url(url: str) -> str:
        """Clean URL to avoid detection of bot-like parameters."""
        # Remove common tracking parameters
        params_to_remove = ['utm_source', 'utm_medium', 'utm_campaign', 'ref', 'source']
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Remove tracking parameters
        for param in params_to_remove:
            query_params.pop(param, None)
        
        # Rebuild URL
        clean_query = urlencode(query_params, doseq=True)
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            clean_query,
            parsed.fragment
        )) 