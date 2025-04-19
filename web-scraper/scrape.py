#!/usr/bin/env python3
"""
Main entry point for the web scraping application.
"""

import argparse
import asyncio
import logging
from pathlib import Path

from scraper.justyol import JustYolScraper
from scraper.api_scraper import JustYolApiScraper
from scraper.selenium_scraper import JustYolSeleniumScraper
from data_processor.cleaner import clean_product_data
from data_processor.standardizer import standardize_products
from data_processor.output import save_to_csv, save_to_json, save_to_sqlite

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the scraper."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Web scraper for e-commerce sites')
    parser.add_argument('--url', type=str, 
                        default='https://justyol.com/en/collections/women-handbags',
                        help='URL to scrape')
    parser.add_argument('--pages', type=int, default=2,
                        help='Number of pages to scrape')
    parser.add_argument('--output', type=str, default='csv,json',
                        help='Output format(s), comma-separated (csv,json,db)')
    parser.add_argument('--db', type=str, default='products.db',
                        help='SQLite database file')
    parser.add_argument('--method', type=str, default='auto',
                        choices=['api', 'selenium', 'playwright', 'auto'],
                        help='Scraping method to use')
    args = parser.parse_args()

    products = []
    
    # Try different scraping methods based on the specified method or in sequence if auto
    if args.method == 'auto' or args.method == 'api':
        logger.info("Attempting API-based scraping")
        api_scraper = JustYolApiScraper()
        api_products = api_scraper.scrape_products(args.url)
        
        if api_products and len(api_products) > 3:
            logger.info(f"Successfully retrieved {len(api_products)} products via API")
            products = api_products
        elif args.method == 'api':
            logger.warning("API-based scraping failed")
        else:
            logger.info("API-based scraping failed, trying Selenium")
    
    if (args.method == 'auto' and not products) or args.method == 'selenium':
        logger.info("Attempting Selenium-based scraping")
        selenium_scraper = JustYolSeleniumScraper()
        selenium_products = selenium_scraper.scrape_products(args.url, args.pages)
        
        if selenium_products and len(selenium_products) > 3:
            logger.info(f"Successfully retrieved {len(selenium_products)} products via Selenium")
            products = selenium_products
        elif args.method == 'selenium':
            logger.warning("Selenium-based scraping failed")
        else:
            logger.info("Selenium-based scraping failed, trying Playwright")
    
    if (args.method == 'auto' and not products) or args.method == 'playwright':
        logger.info("Attempting Playwright-based scraping")
        playwright_scraper = JustYolScraper()
        
        try:
            # Start the browser
            await playwright_scraper.start()
            
            # Scrape the products
            playwright_products = await playwright_scraper.scrape_products(args.url, args.pages)
            
            if playwright_products and len(playwright_products) > 3:
                logger.info(f"Successfully retrieved {len(playwright_products)} products via Playwright")
                products = playwright_products
            else:
                logger.warning("Playwright-based scraping failed")
        except Exception as e:
            logger.error(f"An error occurred during Playwright scraping: {e}")
        finally:
            # Close the browser
            await playwright_scraper.stop()
    
    if not products:
        logger.error("All scraping methods failed")
        return
    
    # Standardize the product data
    standardized_products = standardize_products(products)
    logger.info(f"Standardized {len(standardized_products)} products")
    
    # Clean the data
    cleaned_products = clean_product_data(standardized_products)
    logger.info("Data cleaning completed")
    
    # Save the data in requested formats
    output_formats = args.output.split(',')
    
    if 'csv' in output_formats:
        csv_path = save_to_csv(cleaned_products, 'products.csv')
        logger.info(f"Data saved to CSV: {csv_path}")
        
    if 'json' in output_formats:
        json_path = save_to_json(cleaned_products, 'products.json')
        logger.info(f"Data saved to JSON: {json_path}")
        
    if 'db' in output_formats:
        db_path = save_to_sqlite(cleaned_products, args.db)
        logger.info(f"Data saved to SQLite database: {db_path}")
    
    logger.info("Scraping completed successfully")

if __name__ == "__main__":
    asyncio.run(main())
