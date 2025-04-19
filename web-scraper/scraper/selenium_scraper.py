"""
Selenium-based scraper for JustYol.
"""

import logging
import time
import json
import re
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class JustYolSeleniumScraper:
    """Scraper that uses Selenium to monitor network requests and extract JustYol product data."""
    
    def __init__(self, headless: bool = True):
        """
        Initialize the Selenium scraper.
        
        Args:
            headless: Whether to run the browser in headless mode
        """
        self.headless = headless
    
    def scrape_products(self, url: str, pages: int = 1) -> List[Dict[str, Any]]:
        """
        Scrape product information using Selenium to monitor network requests.
        
        Args:
            url: The collection URL
            pages: Number of pages to scrape
            
        Returns:
            A list of dictionaries containing product information
        """
        # Set up Chrome options
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-infobars")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36')
        
        # Enable DevTools Protocol
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        try:
            logger.info("Monitoring network requests...")
            driver.get(url)
            time.sleep(5)  # Wait for initial load
            
            # Scroll down to trigger more requests
            for _ in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Extract network logs
            logs = driver.get_log('performance')
            
            # Look for XHR/Fetch requests with product data
            api_responses = []
            for log in logs:
                try:
                    log_entry = json.loads(log["message"])["message"]
                    if "Network.responseReceived" in log_entry["method"]:
                        request_id = log_entry["params"]["requestId"]
                        resp_url = log_entry["params"]["response"]["url"]
                        if "products" in resp_url and ("json" in resp_url or "api" in resp_url):
                            logger.info(f"Found product API call: {resp_url}")
                            api_responses.append((request_id, resp_url))
                except:
                    continue
                    
            # Extract data from responses
            for request_id, resp_url in api_responses:
                try:
                    response = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                    data = json.loads(response["body"])
                    if "products" in data:
                        logger.info(f"Found product data in response!")
                        return data["products"]
                except:
                    continue
                    
            # If we couldn't find API calls, scrape from the page
            logger.info("Could not find product API calls, falling back to visible products...")
            
            # Try going through multiple pages
            all_products = []
            for page in range(1, pages + 1):
                try:
                    page_url = f"{url}?page={page}" if "?" not in url else f"{url}&page={page}"
                    driver.get(page_url)
                    time.sleep(5)  # Wait for page to load
                    
                    # Check if we're still on a valid page
                    if "page not found" in driver.title.lower() or "404" in driver.title.lower():
                        break
                    
                    # Find all products on the page
                    product_cards = driver.find_elements(By.CSS_SELECTOR, '.product-card')
                    if not product_cards:
                        # Try alternative selectors
                        product_cards = driver.find_elements(By.CSS_SELECTOR, 'div.hdt-card-product')
                        
                    if not product_cards:
                        break
                        
                    logger.info(f"Found {len(product_cards)} products on page {page}")
                    
                    # Extract product data
                    for card in product_cards:
                        try:
                            product = {}
                            
                            # Extract product name and URL
                            name_el = None
                            try:
                                name_el = card.find_element(By.CSS_SELECTOR, '.product-card-title')
                            except:
                                try:
                                    name_el = card.find_element(By.CSS_SELECTOR, 'a.hdt-card-product__title')
                                except:
                                    pass
                                    
                            if name_el:
                                product["name"] = name_el.text.strip()
                                
                                # Try to get URL
                                try:
                                    url_el = name_el if name_el.tag_name == 'a' else card.find_element(By.CSS_SELECTOR, 'a')
                                    product_url = url_el.get_attribute("href")
                                    if product_url:
                                        product["url"] = product_url
                                except:
                                    pass
                            
                            # Extract brand
                            try:
                                brand_el = card.find_element(By.CSS_SELECTOR, '.product-card-vendor')
                                product["brand"] = brand_el.text.strip()
                            except:
                                pass
                            
                            # Extract price
                            try:
                                price_el = card.find_element(By.CSS_SELECTOR, '.sale-price')
                                product["price"] = price_el.text.strip()
                            except:
                                try:
                                    price_el = card.find_element(By.CSS_SELECTOR, '.product-card-price')
                                    product["price"] = price_el.text.strip()
                                except:
                                    product["price"] = "N/A"
                            
                            # Extract original price
                            try:
                                original_price_el = card.find_element(By.CSS_SELECTOR, '.compare-at-price')
                                product["original_price"] = original_price_el.text.strip()
                            except:
                                product["original_price"] = product.get("price", "N/A")
                            
                            # Extract discount
                            try:
                                discount_el = card.find_element(By.CSS_SELECTOR, '.product-card-badge.sale')
                                product["discount"] = discount_el.text.strip()
                            except:
                                pass
                            
                            # Extract image
                            try:
                                img_el = card.find_element(By.TAG_NAME, 'img')
                                img_url = img_el.get_attribute("src") or img_el.get_attribute("data-src")
                                if img_url:
                                    if img_url.startswith("//"):
                                        img_url = "https:" + img_url
                                    product["image_url"] = img_url
                            except:
                                pass
                            
                            # Only add products with at least a name
                            if "name" in product:
                                all_products.append(product)
                        except Exception as e:
                            logger.warning(f"Error extracting product: {str(e)}")
                            continue
                except Exception as e:
                    logger.warning(f"Error processing page {page}: {str(e)}")
                    break
                    
            return all_products
                
        except Exception as e:
            logger.error(f"Error monitoring network: {str(e)}")
            return []
        finally:
            driver.quit()
