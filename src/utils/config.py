import os
from typing import Dict
from dotenv import load_dotenv

class Config:
    """Configuration manager for the application."""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # API Keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Scraper Settings
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.retry_delay = int(os.getenv('RETRY_DELAY', '2'))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        
        # Rate Limits
        self.rate_limits: Dict[str, int] = {
            'Nike': int(os.getenv('NIKE_RATE_LIMIT', '60')),
            'Foot Locker': int(os.getenv('FOOTLOCKER_RATE_LIMIT', '60')),
            'Finish Line': int(os.getenv('FINISHLINE_RATE_LIMIT', '60')),
            "Dick's Sporting Goods": int(os.getenv('DICKS_RATE_LIMIT', '60'))
        }
    
    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required but not set in environment")
        return True

# Create a singleton instance
config = Config() 