"""
JustYol-specific implementation of the BaseScraper.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Page

from scraper.base import BaseScraper

logger = logging.getLogger(__name__)

class JustYolScraper(BaseScraper):
    """Scraper for JustYol product listings."""
    
    def __init__(self, headless: bool = True):
        """
        Initialize the JustYol scraper.
        
        Args:
            headless: Whether to run the browser in headless mode
        """
        self.headless = headless
        self.browser = None
        self.context = None
    
    async def start(self) -> None:
        """Start the browser and create a new context."""
        logger.info("Starting browser")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    
    async def stop(self) -> None:
        """Close the browser and clean up resources."""
        if self.browser:
            logger.info("Closing browser")
            await self.browser.close()
            await self.playwright.stop()
    
    async def scrape_products(self, url: str, pages: int = 1) -> List[Dict[str, Any]]:
        """
        Scrape product information from JustYol search results.
        
        Args:
            url: The JustYol collection URL
            pages: Number of pages to scrape
            
        Returns:
            A list of dictionaries containing product information
        """
        products = []
        page = await self.context.new_page()
        
        # Navigate to the initial URL
        await page.goto(url, wait_until="networkidle")
        logger.info(f"Navigated to {url}")
        
        # Scrape the specified number of pages
        for i in range(pages):
            logger.info(f"Scraping page {i+1} of {pages}")
            
            # Extract products from the current page
            page_products = await self._extract_products(page)
            products.extend(page_products)
            
            # Go to the next page if not on the last page
            if i < pages - 1:
                has_next = await self._go_to_next_page(page)
                if not has_next:
                    logger.info("No more pages available")
                    break
                
                # Wait for the page to load
                await page.wait_for_load_state("networkidle")
                
                # Add a delay to avoid being blocked
                await asyncio.sleep(2)
        
        return products
    
    async def _extract_products(self, page: Page) -> List[Dict[str, Any]]:
        """
        Extract product information from the current page.
        
        Args:
            page: The Playwright page object
            
        Returns:
            A list of dictionaries containing product information
        """
        products = []
        
        # Wait for the product grid to load
        await page.wait_for_selector('.product-card', timeout=10000)
        
        # Get all product elements
        product_elements = await page.query_selector_all('.product-card')
        
        for element in product_elements:
            try:
                # Extract product name
                name_element = await element.query_selector('.product-card-title')
                name = await name_element.inner_text() if name_element else None
                
                # Extract brand
                brand_element = await element.query_selector('.product-card-vendor')
                brand = await brand_element.inner_text() if brand_element else None
                
                # Extract product URL
                url_element = await element.query_selector('a.product-card-image-wrapper')
                relative_url = await url_element.get_attribute('href') if url_element else None
                product_url = f"https://justyol.com{relative_url}" if relative_url else None
                
                # Extract current price
                price_element = await element.query_selector('.product-card-price .sale-price')
                price = await price_element.inner_text() if price_element else None
                
                # Extract original price
                original_price_element = await element.query_selector('.product-card-price .compare-at-price')
                original_price = await original_price_element.inner_text() if original_price_element else price
                
                # Extract discount percentage
                discount_element = await element.query_selector('.product-card-badge.sale')
                discount = await discount_element.inner_text() if discount_element else None
                
                # Extract image URL
                img_element = await element.query_selector('img.product-card-image')
                img_url = await img_element.get_attribute('src') if img_element else None
                if img_url and img_url.startswith('//'):
                    img_url = f"https:{img_url}"
                
                # Only add products with at least a name
                if name:
                    products.append({
                        'name': name,
                        'brand': brand,
                        'price': price,
                        'original_price': original_price,
                        'discount': discount,
                        'url': product_url,
                        'image_url': img_url
                    })
            except Exception as e:
                logger.warning(f"Error extracting product: {e}")
                continue
        
        logger.info(f"Extracted {len(products)} products from the current page")
        return products
    
    async def _go_to_next_page(self, page: Page) -> bool:
        """
        Navigate to the next page of results.
        
        Args:
            page: The Playwright page object
            
        Returns:
            True if successfully navigated to the next page, False otherwise
        """
        try:
            # Look for the "Next" button
            next_button = await page.query_selector('a.pagination__item--next')
            
            if next_button:
                # Check if the button is disabled
                is_disabled = await next_button.get_attribute('aria-disabled')
                if is_disabled == 'true':
                    return False
                
                # Click the next button
                await next_button.click()
                return True
            else:
                # Try alternative pagination if the standard one isn't found
                load_more_button = await page.query_selector('button.load-more')
                if load_more_button:
                    await load_more_button.click()
                    return True
                
                return False
        except Exception as e:
            logger.warning(f"Error navigating to next page: {e}")
            return False
