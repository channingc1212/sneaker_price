from bs4 import BeautifulSoup
from typing import List
import urllib.parse
import logging
import json
import re

from .base_scraper import BaseScraper, SneakerProduct

logger = logging.getLogger(__name__)

class NikeScraper(BaseScraper):
    """Scraper for Nike website."""
    
    def __init__(self):
        super().__init__("https://www.nike.com")
        
    async def search_product(self, query: str, **kwargs) -> List[SneakerProduct]:
        """Search for sneakers on Nike's website."""
        try:
            encoded_query = urllib.parse.quote(query)
            search_url = f"{self.base_url}/w/mens-shoes?q={encoded_query}"
            logger.info(f"Searching Nike with URL: {search_url}")
            
            html_content = await self._make_request(search_url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for the product grid
            products = []
            
            # Try to find products in the modern Nike layout
            product_cards = soup.find_all('div', {'class': 'product-card'}) or \
                          soup.find_all('div', {'class': 'product-grid__items'}) or \
                          soup.find_all('div', {'class': 'product-grid__item'})
            
            logger.info(f"Found {len(product_cards)} product cards on Nike")
            
            for card in product_cards:
                try:
                    # Try different possible selectors for product information
                    name = (
                        card.find('h3', {'class': 'product-card__title'}) or
                        card.find('h3', {'class': 'product-card__name'}) or
                        card.find('div', {'class': 'product-card__title'})
                    )
                    if name:
                        name = name.text.strip()
                    
                    # Try to find price
                    price_elem = (
                        card.find('div', {'class': 'product-price'}) or
                        card.find('div', {'class': 'product-card__price'}) or
                        card.find('span', {'class': 'product-price'})
                    )
                    if price_elem:
                        price = self.clean_price(price_elem.text)
                    else:
                        continue
                    
                    # Try to find URL
                    url_elem = card.find('a')
                    if url_elem and 'href' in url_elem.attrs:
                        url = url_elem['href']
                        if not url.startswith('http'):
                            url = self.base_url + url
                    else:
                        continue
                    
                    # Try to find image
                    image = (
                        card.find('img', {'class': 'product-card__hero-image'}) or
                        card.find('img', {'class': 'product-card__image'}) or
                        card.find('img')
                    )
                    image_url = image['src'] if image and 'src' in image.attrs else None
                    
                    product = SneakerProduct(
                        name=name,
                        price=price,
                        url=url,
                        store="Nike",
                        image_url=image_url
                    )
                    products.append(product)
                    logger.debug(f"Successfully parsed Nike product: {name}")
                    
                except Exception as e:
                    logger.error(f"Error parsing Nike product card: {str(e)}")
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"Error searching Nike: {str(e)}")
            return []
    
    async def get_product_details(self, url: str) -> SneakerProduct:
        """Get detailed information about a specific Nike product."""
        try:
            html_content = await self._make_request(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try to find product name
            name = (
                soup.find('h1', {'class': 'product-title'}) or
                soup.find('h1', {'id': 'pdp_product_title'})
            )
            name = name.text.strip() if name else ""
            
            # Try to find price
            price_elem = (
                soup.find('div', {'class': 'product-price'}) or
                soup.find('div', {'class': 'css-b9fpep'})  # Nike's price container class
            )
            price = self.clean_price(price_elem.text) if price_elem else 0.0
            
            # Try to find available sizes
            size_container = (
                soup.find('div', {'class': 'size-selector'}) or
                soup.find('div', {'class': 'mt2-sm css-12whm6j'})  # Nike's size grid
            )
            
            available_sizes = []
            if size_container:
                size_buttons = size_container.find_all('button')
                available_sizes = [
                    btn.text.strip() 
                    for btn in size_buttons 
                    if 'disabled' not in btn.attrs.get('class', [])
                ]
            
            # Try to find color
            color = (
                soup.find('div', {'class': 'product-color'}) or
                soup.find('li', {'class': 'description-preview__color-description'})
            )
            color = color.text.strip() if color else ""
            
            # Check availability
            out_of_stock = (
                soup.find('div', {'class': 'out-of-stock'}) or
                soup.find('div', {'class': 'product-status'})
            )
            availability = not bool(out_of_stock)
            
            return SneakerProduct(
                name=name,
                price=price,
                url=url,
                store="Nike",
                size=','.join(available_sizes),
                color=color,
                availability=availability
            )
            
        except Exception as e:
            logger.error(f"Error getting Nike product details: {str(e)}")
            raise 