from bs4 import BeautifulSoup
from typing import List
import urllib.parse

from .base_scraper import BaseScraper, SneakerProduct

class FootLockerScraper(BaseScraper):
    """Scraper for Foot Locker website."""
    
    def __init__(self):
        super().__init__("https://www.footlocker.com")
        
    async def search_product(self, query: str, **kwargs) -> List[SneakerProduct]:
        """Search for sneakers on Foot Locker's website."""
        encoded_query = urllib.parse.quote(query)
        search_url = f"{self.base_url}/search?query={encoded_query}"
        html_content = await self._make_request(search_url)
        
        products = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Note: Selectors need to be updated based on Foot Locker's actual HTML structure
        product_cards = soup.find_all('div', class_='ProductCard')
        
        for card in product_cards:
            try:
                name = card.find('span', class_='ProductName').text.strip()
                price_elem = card.find('span', class_='ProductPrice')
                price = self.clean_price(price_elem.text)
                url = self.base_url + card.find('a')['href']
                image = card.find('img')['src']
                
                product = SneakerProduct(
                    name=name,
                    price=price,
                    url=url,
                    store="Foot Locker",
                    image_url=image
                )
                products.append(product)
            except Exception as e:
                continue
                
        return products
    
    async def get_product_details(self, url: str) -> SneakerProduct:
        """Get detailed information about a specific Foot Locker product."""
        html_content = await self._make_request(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            name = soup.find('h1', class_='ProductName').text.strip()
            price_elem = soup.find('span', class_='ProductPrice')
            price = self.clean_price(price_elem.text)
            
            # Get available sizes
            size_container = soup.find('div', class_='SizeContainer')
            available_sizes = []
            if size_container:
                size_buttons = size_container.find_all('button', {'aria-disabled': 'false'})
                available_sizes = [btn.text.strip() for btn in size_buttons]
            
            # Get color
            color = soup.find('span', class_='ProductColor').text.strip()
            
            # Check availability
            out_of_stock = soup.find('span', class_='OutOfStock')
            availability = not bool(out_of_stock)
            
            return SneakerProduct(
                name=name,
                price=price,
                url=url,
                store="Foot Locker",
                size=','.join(available_sizes),
                color=color,
                availability=availability
            )
        except Exception as e:
            raise Exception(f"Failed to parse product details: {str(e)}") 