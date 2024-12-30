import streamlit as st
from src.scrapers.base_scraper import SneakerProduct

def display_sneaker_card(product: SneakerProduct):
    """Display a single sneaker product card."""
    with st.container():
        cols = st.columns([2, 1, 1])
        
        # Column 1: Image and Name
        with cols[0]:
            if product.image_url:
                st.image(product.image_url, width=200)
            st.subheader(product.name)
        
        # Column 2: Details
        with cols[1]:
            st.markdown(f"**Price:** ${product.price:.2f}")
            st.markdown(f"**Store:** {product.store}")
            if product.size:
                st.markdown(f"**Available Sizes:** {product.size}")
            if product.color:
                st.markdown(f"**Color:** {product.color}")
        
        # Column 3: Status and Action
        with cols[2]:
            status = "✅ In Stock" if product.availability else "❌ Out of Stock"
            st.markdown(f"**Status:** {status}")
            st.link_button("View on Store", product.url)
        
        st.divider()

def display_ai_analysis(analysis: dict):
    """Display AI analysis of the sneaker search."""
    with st.expander("🤖 AI Analysis", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Identified Details:**")
            st.json({
                "Brand": analysis.get("brand"),
                "Model": analysis.get("model")
            })
        
        with col2:
            st.markdown("**Search Suggestions:**")
            for term in analysis.get("suggested_terms", []):
                st.markdown(f"- {term}")

def display_error_message(error: str):
    """Display an error message in a consistent format."""
    st.error(f"😕 {error}")

def display_loading_message(message: str):
    """Display a loading message with spinner."""
    return st.spinner(f"🔄 {message}") 