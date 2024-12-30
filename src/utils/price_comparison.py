import asyncio
from typing import List, Type

from ..scrapers.base_scraper import BaseScraper, SneakerProduct

class PriceComparisonService:
    """Service to aggregate and compare prices from different sources."""
    
    def __init__(self, scrapers: List[Type[BaseScraper]]):
        self.scrapers = [scraper() for scraper in scrapers]
    
    async def compare_prices(self, query: str, **kwargs) -> List[SneakerProduct]:
        """
        Search for a sneaker across all configured scrapers and return results.
        
        Args:
            query: Search query for the sneaker
            **kwargs: Additional search parameters (size, color, etc.)
            
        Returns:
            List of SneakerProduct objects sorted by price
        """
        tasks = []
        for scraper in self.scrapers:
            tasks.append(scraper.search_product(query, **kwargs))
        
        # Gather results from all scrapers
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and filter out errors
        products = []
        for result in results:
            if isinstance(result, List):
                products.extend(result)
        
        # Sort products by price
        return sorted(products, key=lambda x: x.price)
    
    async def get_product_details(self, products: List[SneakerProduct]) -> List[SneakerProduct]:
        """Fetch detailed information for a list of products."""
        tasks = []
        for product in products:
            for scraper in self.scrapers:
                if scraper.base_url in product.url:
                    tasks.append(scraper.get_product_details(product.url))
                    break
        
        detailed_products = await asyncio.gather(*tasks, return_exceptions=True)
        return [p for p in detailed_products if isinstance(p, SneakerProduct)] 