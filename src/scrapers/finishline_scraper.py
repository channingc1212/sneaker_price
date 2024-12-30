from bs4 import BeautifulSoup
from typing import List
import urllib.parse

from .base_scraper import BaseScraper, SneakerProduct

class FinishLineScraper(BaseScraper):
    """Scraper for Finish Line website."""
    
    def __init__(self):
        super().__init__("https://www.finishline.com")
        
    async def search_product(self, query: str, **kwargs) -> List[SneakerProduct]:
        """Search for sneakers on Finish Line's website."""
        encoded_query = urllib.parse.quote(query)
        search_url = f"{self.base_url}/store/search?query={encoded_query}"
        html_content = await self._make_request(search_url)
        
        products = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Note: Selectors need to be updated based on Finish Line's actual HTML structure
        product_cards = soup.find_all('div', class_='product-card')
        
        for card in product_cards:
            try:
                name = card.find('div', class_='product-name').text.strip()
                price_elem = card.find('span', class_='product-price')
                price = self.clean_price(price_elem.text)
                url = self.base_url + card.find('a', class_='product-link')['href']
                image = card.find('img', class_='product-image')['src']
                
                product = SneakerProduct(
                    name=name,
                    price=price,
                    url=url,
                    store="Finish Line",
                    image_url=image
                )
                products.append(product)
            except Exception as e:
                continue
                
        return products
    
    async def get_product_details(self, url: str) -> SneakerProduct:
        """Get detailed information about a specific Finish Line product."""
        html_content = await self._make_request(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            name = soup.find('h1', class_='product-title').text.strip()
            price_elem = soup.find('span', class_='current-price')
            price = self.clean_price(price_elem.text)
            
            # Get available sizes
            size_container = soup.find('div', class_='size-selector')
            available_sizes = []
            if size_container:
                size_buttons = size_container.find_all('button', {'data-available': 'true'})
                available_sizes = [btn.text.strip() for btn in size_buttons]
            
            # Get color
            color = soup.find('span', class_='selected-color').text.strip()
            
            # Check availability
            availability = bool(available_sizes)
            
            return SneakerProduct(
                name=name,
                price=price,
                url=url,
                store="Finish Line",
                size=','.join(available_sizes),
                color=color,
                availability=availability
            )
        except Exception as e:
            raise Exception(f"Failed to parse product details: {str(e)}") 