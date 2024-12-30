import streamlit as st
import sys
import logging
from src.utils.setup_check import verify_setup
from src.utils.config import config  # This will load environment variables
from ui.pages.home import main

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Verify setup before running
        if not verify_setup():
            logger.error("❌ Setup verification failed. Please check the errors above.")
            sys.exit(1)
        
        logger.info("✅ Setup verification passed. Starting application...")
        main()
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1) 