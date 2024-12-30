import streamlit as st
import asyncio
import logging
from typing import List, Optional
import json

from src.api.openai_service import OpenAIService
from src.utils.config import config
from src.scrapers.base_scraper import SneakerProduct
from src.utils.price_comparison import PriceComparisonService
from src.scrapers.nike_scraper import NikeScraper
from src.scrapers.footlocker_scraper import FootLockerScraper
from src.scrapers.finishline_scraper import FinishLineScraper
from src.scrapers.dicks_scraper import DicksScraper

from ..components.sneaker_card import (
    display_sneaker_card,
    display_ai_analysis,
    display_error_message,
    display_loading_message
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
SCRAPERS = {
    "Nike": NikeScraper,
    "Foot Locker": FootLockerScraper,
    "Finish Line": FinishLineScraper,
    "Dick's Sporting Goods": DicksScraper
}

# Initialize services only if they haven't been initialized
if 'comparison_service' not in st.session_state:
    st.session_state.comparison_service = PriceComparisonService([scraper for scraper in SCRAPERS.values()])
if 'ai_service' not in st.session_state:
    st.session_state.ai_service = OpenAIService()

async def search_sneakers(query: str, size: Optional[str] = None, color: Optional[str] = None) -> List[SneakerProduct]:
    """Search for sneakers across all platforms."""
    try:
        logger.info(f"Starting search for query: {query}")
        
        # Get AI analysis
        try:
            sneaker_details = await st.session_state.ai_service.identify_sneaker(query)
            st.session_state['ai_analysis'] = sneaker_details
            logger.info(f"AI Analysis complete: {sneaker_details}")
        except Exception as e:
            logger.error(f"Error during AI analysis: {str(e)}")
            display_error_message("Error analyzing sneaker details. Please try again.")
            return []
        
        # Get suggested websites
        try:
            suggested_sites_response = await st.session_state.ai_service.suggest_websites(sneaker_details)
            logger.info(f"Raw suggested sites response: {suggested_sites_response}")
            
            # Handle different response formats
            if isinstance(suggested_sites_response, dict):
                if 'relevantWebsites' in suggested_sites_response:
                    # Handle array of strings
                    if isinstance(suggested_sites_response['relevantWebsites'], list) and \
                       all(isinstance(x, str) for x in suggested_sites_response['relevantWebsites']):
                        suggested_sites = suggested_sites_response['relevantWebsites']
                    # Handle array of objects
                    elif isinstance(suggested_sites_response['relevantWebsites'], list) and \
                         all(isinstance(x, dict) for x in suggested_sites_response['relevantWebsites']):
                        suggested_sites = [site['name'] for site in suggested_sites_response['relevantWebsites']]
                elif 'relevant_websites' in suggested_sites_response:
                    suggested_sites = [site['name'] for site in suggested_sites_response['relevant_websites']]
                else:
                    suggested_sites = list(SCRAPERS.keys())
            else:
                suggested_sites = list(SCRAPERS.keys())
                
            logger.info(f"Processed suggested sites: {suggested_sites}")
            
        except Exception as e:
            logger.error(f"Error getting suggested sites: {str(e)}")
            suggested_sites = list(SCRAPERS.keys())  # Fallback to all sites
        
        # Update active scrapers
        active_scrapers = [SCRAPERS[site] for site in suggested_sites if site in SCRAPERS]
        if not active_scrapers:
            logger.warning("No valid scrapers found, falling back to all scrapers")
            active_scrapers = list(SCRAPERS.values())
            
        st.session_state.comparison_service.scrapers = [scraper() for scraper in active_scrapers]
        
        # Search across platforms
        results = []
        for scraper in st.session_state.comparison_service.scrapers:
            try:
                enhanced_query = await st.session_state.ai_service.enhance_search_query(
                    sneaker_details['normalized_name'],
                    scraper.__class__.__name__
                )
                logger.info(f"Enhanced query for {scraper.__class__.__name__}: {enhanced_query}")
                
                partial_results = await scraper.search_product(
                    enhanced_query,
                    size=size,
                    color=color
                )
                logger.info(f"Found {len(partial_results)} results from {scraper.__class__.__name__}")
                results.extend(partial_results)
            except Exception as e:
                logger.error(f"Error searching {scraper.__class__.__name__}: {str(e)}")
                continue
        
        if not results:
            logger.warning("No results found from any scraper")
            
        return sorted(results, key=lambda x: x.price)
    
    except Exception as e:
        logger.error(f"Unexpected error during search: {str(e)}")
        display_error_message(f"An unexpected error occurred: {str(e)}")
        return []

def main():
    """Main Streamlit application."""
    try:
        st.set_page_config(
            page_title="Sneaker Price Comparison",
            page_icon="👟",
            layout="wide"
        )
    except Exception:
        # Page config already set
        pass
    
    # Header
    st.title("👟 AI-Powered Sneaker Price Comparison")
    st.markdown("""
    Find the best deals on sneakers across multiple retailers.
    Just describe the sneaker you're looking for, and our AI will help find it!
    """)
    
    # Search Form
    with st.form("search_form"):
        query = st.text_input(
            "Describe the sneaker:",
            placeholder="e.g., 'Looking for the latest Jordan 1 High OG in University Blue'"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            size = st.text_input("Size (optional):", placeholder="e.g., 10.5")
        with col2:
            color = st.text_input("Color (optional):", placeholder="e.g., Black")
        
        submitted = st.form_submit_button("🔍 Search")
    
    # Handle search
    if submitted:
        if not query:
            st.warning("Please enter a sneaker description")
        else:
            with display_loading_message("Searching across stores..."):
                try:
                    results = asyncio.run(search_sneakers(
                        query,
                        size=size if size else None,
                        color=color if color else None
                    ))
                    
                    # Display AI analysis if available
                    if 'ai_analysis' in st.session_state:
                        display_ai_analysis(st.session_state['ai_analysis'])
                    
                    # Display results
                    if results:
                        st.success(f"Found {len(results)} results")
                        for product in results:
                            display_sneaker_card(product)
                    else:
                        st.warning("No results found. Try a different description.")
                        
                except Exception as e:
                    logger.error(f"Error during search execution: {str(e)}")
                    display_error_message("An error occurred while searching. Please try again.")
    
    # Footer
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit and OpenAI")

if __name__ == "__main__":
    main() 