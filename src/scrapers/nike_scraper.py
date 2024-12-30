from bs4 import BeautifulSoup
from typing import List

from .base_scraper import BaseScraper, SneakerProduct

class NikeScraper(BaseScraper):
    """Scraper for Nike website."""
    
    def __init__(self):
        super().__init__("https://www.nike.com")
        
    async def search_product(self, query: str, **kwargs) -> List[SneakerProduct]:
        """Search for sneakers on Nike's website."""
        search_url = f"{self.base_url}/w?q={query}"
        html_content = await self._make_request(search_url)
        
        products = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Note: Selectors would need to be updated based on Nike's actual HTML structure
        product_cards = soup.find_all('div', class_='product-card')
        
        for card in product_cards:
            try:
                name = card.find('h3', class_='product-name').text.strip()
                price_elem = card.find('div', class_='product-price')
                price = self.clean_price(price_elem.text)
                url = self.base_url + card.find('a')['href']
                image = card.find('img')['src']
                
                product = SneakerProduct(
                    name=name,
                    price=price,
                    url=url,
                    store="Nike",
                    image_url=image
                )
                products.append(product)
            except Exception as e:
                continue
                
        return products
    
    async def get_product_details(self, url: str) -> SneakerProduct:
        """Get detailed information about a specific Nike product."""
        html_content = await self._make_request(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Note: Selectors would need to be updated based on Nike's actual HTML structure
        try:
            name = soup.find('h1', class_='product-name').text.strip()
            price_elem = soup.find('div', class_='product-price')
            price = self.clean_price(price_elem.text)
            
            # Get available sizes
            sizes = soup.find_all('div', class_='size-option')
            available_sizes = [size.text.strip() for size in sizes if 'disabled' not in size.get('class', [])]
            
            # Get color
            color = soup.find('div', class_='color-description').text.strip()
            
            return SneakerProduct(
                name=name,
                price=price,
                url=url,
                store="Nike",
                size=','.join(available_sizes),
                color=color,
                availability=bool(available_sizes)
            )
        except Exception as e:
            raise Exception(f"Failed to parse product details: {str(e)}") 