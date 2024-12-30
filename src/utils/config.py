import os
from typing import Dict
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """Configuration manager for the application."""
    
    def __init__(self):
        # Load environment variables from .env file
        env_path = Path(__file__).parent.parent.parent / "config" / ".env"
        if not env_path.exists():
            raise ValueError(f"Environment file not found at {env_path}")
        
        load_dotenv(env_path)
        
        # API Keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
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
    
    @classmethod
    def get_instance(cls):
        """Get or create singleton instance."""
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance

# Create a singleton instance
config = Config.get_instance() 