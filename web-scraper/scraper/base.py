"""
Base scraper class that defines the interface for all scrapers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseScraper(ABC):
    """Abstract base class for web scrapers."""
    
    @abstractmethod
    async def start(self) -> None:
        """Initialize the scraper and start the browser."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Clean up resources and close the browser."""
        pass
    
    @abstractmethod
    async def scrape_products(self, url: str, pages: int = 1) -> List[Dict[str, Any]]:
        """
        Scrape product information from the given URL.
        
        Args:
            url: The URL to scrape
            pages: Number of pages to scrape
            
        Returns:
            A list of dictionaries containing product information
        """
        pass
