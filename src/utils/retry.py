import asyncio
import time
from functools import wraps
from typing import Callable, TypeVar, Any
import logging

from .config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    async def acquire(self):
        """Acquire a rate limit slot."""
        now = time.time()
        
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]
        
        if len(self.calls) >= self.calls_per_minute:
            # Wait until we can make another call
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, waiting {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
        
        self.calls.append(now)

class RetryException(Exception):
    """Exception indicating that a retry is needed."""
    pass

def with_retry(
    max_retries: int = None,
    retry_delay: int = None,
    rate_limiter: RateLimiter = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retrying failed operations with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Base delay between retries in seconds
        rate_limiter: Optional rate limiter for API calls
    """
    max_retries = max_retries or config.max_retries
    retry_delay = retry_delay or config.retry_delay
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    # Apply rate limiting if configured
                    if rate_limiter:
                        await rate_limiter.acquire()
                    
                    return await func(*args, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # Calculate exponential backoff delay
                        delay = retry_delay * (2 ** attempt)
                        
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)}. "
                            f"Retrying in {delay} seconds..."
                        )
                        
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
                        raise last_exception
            
            raise last_exception  # Should never reach here
        
        return wrapper
    
    return decorator 