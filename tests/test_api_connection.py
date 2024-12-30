import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent
ENV_PATH = ROOT_DIR / "config" / ".env"

async def test_openai_connection():
    """Test OpenAI API connection with current key."""
    try:
        # Load environment variables from config/.env
        if not load_dotenv(ENV_PATH):
            print(f"❌ Error: .env file not found at {ENV_PATH}")
            return False
            
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("❌ Error: OPENAI_API_KEY not found in environment")
            return False
            
        print(f"✅ Found API key: {api_key[:8]}...{api_key[-4:]}")
            
        # Initialize OpenAI client (using async client for better performance)
        client = AsyncOpenAI(api_key=api_key)
        
        # Try a simple completion
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello! This is a test message."}
            ]
        )
        
        if response.choices[0].message.content:
            print(f"✅ OpenAI API connection successful! Response: {response.choices[0].message.content}")
            return True
            
    except Exception as e:
        print(f"❌ Error connecting to OpenAI API: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_openai_connection()) 