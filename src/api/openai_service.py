import os
from typing import Dict, List, Tuple
from openai import AsyncOpenAI
import json
import logging

from ..utils.config import config

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for AI-powered sneaker identification and search enhancement."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.openai_api_key)

    async def identify_sneaker(self, user_input: str) -> Dict[str, str]:
        """
        Identify sneaker details from user input using GPT.
        Returns structured information about the sneaker.
        """
        try:
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
            
            result = response.choices[0].message.content
            # Validate JSON response
            return json.loads(result)
            
        except Exception as e:
            logger.error(f"Error in identify_sneaker: {str(e)}")
            raise
    
    async def enhance_search_query(self, query: str, website: str) -> str:
        """
        Optimize the search query for a specific website's search patterns.
        """
        try:
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
            
        except Exception as e:
            logger.error(f"Error in enhance_search_query: {str(e)}")
            raise
    
    async def suggest_websites(self, sneaker_details: Dict[str, str]) -> List[str]:
        """
        Suggest the most relevant websites for a particular sneaker.
        """
        try:
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
            
            result = response.choices[0].message.content
            # Validate JSON response
            return json.loads(result)
            
        except Exception as e:
            logger.error(f"Error in suggest_websites: {str(e)}")
            raise 