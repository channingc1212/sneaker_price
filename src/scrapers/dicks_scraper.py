from bs4 import BeautifulSoup
from typing import List
import urllib.parse

from .base_scraper import BaseScraper, SneakerProduct

class DicksScraper(BaseScraper):
    """Scraper for Dick's Sporting Goods website."""
    
    def __init__(self):
        super().__init__("https://www.dickssportinggoods.com")
        
    async def search_product(self, query: str, **kwargs) -> List[SneakerProduct]:
        """Search for sneakers on Dick's Sporting Goods website."""
        encoded_query = urllib.parse.quote(query)
        search_url = f"{self.base_url}/search?query={encoded_query}"
        html_content = await self._make_request(search_url)
        
        products = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Note: Selectors need to be updated based on Dick's actual HTML structure
        product_cards = soup.find_all('div', class_='product-card')
        
        for card in product_cards:
            try:
                name = card.find('a', class_='product-card-title').text.strip()
                price_elem = card.find('span', class_='product-price')
                price = self.clean_price(price_elem.text)
                url = card.find('a', class_='product-card-title')['href']
                if not url.startswith('http'):
                    url = self.base_url + url
                image = card.find('img', class_='product-image')['src']
                
                product = SneakerProduct(
                    name=name,
                    price=price,
                    url=url,
                    store="Dick's Sporting Goods",
                    image_url=image
                )
                products.append(product)
            except Exception as e:
                continue
                
        return products
    
    async def get_product_details(self, url: str) -> SneakerProduct:
        """Get detailed information about a specific Dick's Sporting Goods product."""
        html_content = await self._make_request(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            name = soup.find('h1', class_='product-title').text.strip()
            price_elem = soup.find('span', class_='price-value')
            price = self.clean_price(price_elem.text)
            
            # Get available sizes
            size_container = soup.find('div', class_='size-selector')
            available_sizes = []
            if size_container:
                size_options = size_container.find_all('button', {'data-disabled': 'false'})
                available_sizes = [opt.text.strip() for opt in size_options]
            
            # Get color
            color = soup.find('span', class_='color-label').text.strip()
            
            # Check availability
            out_of_stock = soup.find('div', class_='out-of-stock')
            availability = not bool(out_of_stock)
            
            return SneakerProduct(
                name=name,
                price=price,
                url=url,
                store="Dick's Sporting Goods",
                size=','.join(available_sizes),
                color=color,
                availability=availability
            )
        except Exception as e:
            raise Exception(f"Failed to parse product details: {str(e)}") 