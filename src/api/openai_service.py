import os
from typing import Dict, List, Tuple
from openai import OpenAI

class OpenAIService:
    """Service for AI-powered sneaker identification and search enhancement."""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# The prompt is the specific task or question you want the AI to address 
# The role system content provides context about the AI's identity or expertise, guiding how it should respond to the prompt.
# Pricing: https://openai.com/api/pricing/
    async def identify_sneaker(self, user_input: str) -> Dict[str, str]:
        """
        Identify sneaker details from user input using GPT.
        Returns structured information about the sneaker.
        """
        prompt = f"""
        Analyze this sneaker description and extract key details:
        "{user_input}"
        
        Return only these fields in valid JSON format:
        - brand: The sneaker brand
        - model: The specific model name
        - normalized_name: A standardized name for searching (e.g., "nike-air-max-90")
        - suggested_terms: List of 2-3 alternative search terms
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-2024-11-20", # change this to advanced model
            messages=[
                {"role": "system", "content": "You are a sneaker expert. Extract and normalize sneaker information from user descriptions."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )

        return response.choices[0].message.content
    
    async def enhance_search_query(self, query: str, website: str) -> str:
        """
        Optimize the search query for a specific website's search patterns.
        """
        prompt = f"""
        Optimize this search query: "{query}"
        for the website: {website}
        
        Consider:
        1. Common search patterns on this website
        2. Important keywords to include
        3. Format requirements
        
        Return only the optimized search query text.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-2024-11-20", # change this to advanced model
            messages=[
                {"role": "system", "content": "You are a search optimization expert for sneaker websites."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()
    
    async def suggest_websites(self, sneaker_details: Dict[str, str]) -> List[str]:
        """
        Suggest the most relevant websites for a particular sneaker.
        """
        prompt = f"""
        Given this sneaker:
        Brand: {sneaker_details.get('brand')}
        Model: {sneaker_details.get('model')}
        
        Return a JSON array of the 3 most relevant websites from this list:
        - Foot Locker
        - Finish Line
        - Dick's Sporting Goods
        - Nike
        
        Consider:
        1. Website's typical inventory
        2. Brand partnerships
        3. Likelihood of availability
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-2024-11-20", # change this to advanced model
            messages=[
                {"role": "system", "content": "You are a sneaker retail expert."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        return response.choices[0].message.content 