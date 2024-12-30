import asyncio
import json
import streamlit as st
from typing import List, Dict

from scrapers.nike_scraper import NikeScraper
from scrapers.footlocker_scraper import FootLockerScraper
from scrapers.finishline_scraper import FinishLineScraper
from scrapers.dicks_scraper import DicksScraper
from utils.price_comparison import PriceComparisonService
from api.openai_service import OpenAIService

# Configure the page
st.set_page_config(
    page_title="Sneaker Price Comparison",
    page_icon="👟",
    layout="wide"
)

# Initialize services
SCRAPERS = {
    "Nike": NikeScraper,
    "Foot Locker": FootLockerScraper,
    "Finish Line": FinishLineScraper,
    "Dick's Sporting Goods": DicksScraper
}

service = PriceComparisonService([scraper for scraper in SCRAPERS.values()])
ai_service = OpenAIService()

def display_product(product):
    """Display a single product in the UI."""
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader(product.name)
            if product.image_url:
                st.image(product.image_url, width=200)
        
        with col2:
            st.write(f"**Price:** ${product.price:.2f}")
            st.write(f"**Store:** {product.store}")
            if product.size:
                st.write(f"**Sizes:** {product.size}")
            if product.color:
                st.write(f"**Color:** {product.color}")
        
        with col3:
            st.write("**Status:** " + ("Available" if product.availability else "Out of Stock"))
            st.link_button("View on Store", product.url)
        
        st.divider()

async def process_search(user_input: str, size: str = None, color: str = None) -> List:
    """Process search with AI enhancement and get results."""
    # Use AI to identify sneaker details
    sneaker_details = json.loads(await ai_service.identify_sneaker(user_input))
    
    # Show identified details
    with st.expander("AI-Identified Details"):
        st.json(sneaker_details)
    
    # Get suggested websites
    suggested_sites = json.loads(await ai_service.suggest_websites(sneaker_details))
    
    # Filter scrapers based on AI suggestions
    active_scrapers = [SCRAPERS[site] for site in suggested_sites if site in SCRAPERS]
    service.scrapers = [scraper() for scraper in active_scrapers]
    
    # Enhance search query for each website
    results = []
    for scraper in service.scrapers:
        enhanced_query = await ai_service.enhance_search_query(
            sneaker_details['normalized_name'], 
            scraper.__class__.__name__
        )
        partial_results = await scraper.search_product(
            enhanced_query,
            size=size,
            color=color
        )
        results.extend(partial_results)
    
    # Sort by price
    return sorted(results, key=lambda x: x.price)

# Main UI
st.title("👟 AI-Powered Sneaker Price Comparison")

with st.form("search_form"):
    query = st.text_input(
        "Describe the sneaker:",
        placeholder="e.g., 'I'm looking for the latest Air Jordan 39 in dark color with US size 13 in men's"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        size = st.text_input("Size (optional):", placeholder="e.g., 10.5")
    with col2:
        color = st.text_input("Color (optional):", placeholder="e.g., Black")
    
    submitted = st.form_submit_button("Search")

if submitted and query:
    with st.spinner("AI is analyzing your request and searching across stores..."):
        results = asyncio.run(process_search(
            query,
            size=size if size else None,
            color=color if color else None
        ))
        
        if results:
            st.success(f"Found {len(results)} results")
            for product in results:
                display_product(product)
        else:
            st.warning("No results found. Try a different description.") 