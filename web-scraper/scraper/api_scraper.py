"""
API-based scraper for JustYol.
"""

import logging
import requests
import json
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class JustYolApiScraper:
    """Scraper that uses direct API access to retrieve JustYol product data."""
    
    def __init__(self):
        """Initialize the API scraper."""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://justyol.com/en/collections/women-handbags"
        }
    
    def scrape_products(self, url: str) -> List[Dict[str, Any]]:
        """
        Scrape product information using various API approaches.
        
        Args:
            url: The collection URL
            
        Returns:
            A list of dictionaries containing product information
        """
        # Try all methods one by one
        products = self._get_api_data(url)
        if products and len(products) > 3:
            logger.info(f"Successfully retrieved {len(products)} products via direct API")
            return products
            
        products = self._try_inventory_api(url)
        if products and len(products) > 3:
            logger.info(f"Successfully retrieved {len(products)} products via inventory API")
            return products
            
        products = self._try_graphql_approach(url)
        if products and len(products) > 3:
            logger.info(f"Successfully retrieved {len(products)} products via GraphQL")
            return products
            
        logger.warning("All API approaches failed")
        return []
    
    def _get_api_data(self, url: str) -> Optional[List[Dict[str, Any]]]:
        """
        Attempt to directly access the API if possible.
        
        Args:
            url: The collection URL
            
        Returns:
            A list of product dictionaries if successful, None otherwise
        """
        try:
            # Extract collection handle from URL
            collection_match = re.search(r'collections/([a-zA-Z0-9-]+)', url)
            if not collection_match:
                return None
                
            collection = collection_match.group(1)
            
            # Try different API endpoints that might return product data
            api_urls = [
                f"https://justyol.com/api/collections/{collection}/products.json?limit=250",
                f"https://justyol.com/en/collections/{collection}/products.json?limit=250",
                f"https://justyol.com/collections/{collection}/products.json?limit=250"
            ]
            
            for api_url in api_urls:
                try:
                    logger.info(f"Trying API URL: {api_url}")
                    response = requests.get(api_url, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if 'products' in data:
                                return data['products']
                        except:
                            pass
                except:
                    continue
                    
            return None
        except Exception as e:
            logger.error(f"API approach failed: {str(e)}")
            return None
    
    def _try_inventory_api(self, url: str) -> Optional[List[Dict[str, Any]]]:
        """
        Try to access inventory API endpoints which may contain product data.
        
        Args:
            url: The collection URL
            
        Returns:
            A list of product dictionaries if successful, None otherwise
        """
        try:
            # Extract collection handle from URL
            collection_match = re.search(r'collections/([a-zA-Z0-9-]+)', url)
            if not collection_match:
                return None
                
            collection = collection_match.group(1)
            
            # Some common inventory API endpoints
            inventory_urls = [
                "https://justyol.com/en/products.json?limit=250",
                f"https://justyol.com/api/inventory/products?collection={collection}&limit=250",
                f"https://justyol.com/en/recommendations/products.json?collection={collection}&limit=250"
            ]
            
            for inventory_url in inventory_urls:
                try:
                    logger.info(f"Trying inventory API: {inventory_url}")
                    response = requests.get(inventory_url, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if 'products' in data:
                                return data['products']
                        except:
                            pass
                except:
                    continue
                    
            return None
        except Exception as e:
            logger.error(f"Inventory API approach failed: {str(e)}")
            return None
    
    def _try_graphql_approach(self, url: str) -> Optional[List[Dict[str, Any]]]:
        """
        Try to use GraphQL if the site uses it.
        
        Args:
            url: The collection URL
            
        Returns:
            A list of product dictionaries if successful, None otherwise
        """
        try:
            # Extract collection handle from URL
            collection_match = re.search(r'collections/([a-zA-Z0-9-]+)', url)
            if not collection_match:
                return None
                
            collection = collection_match.group(1)
            
            # Update headers for GraphQL
            graphql_headers = self.headers.copy()
            graphql_headers["Content-Type"] = "application/json"
            
            # Common GraphQL endpoint
            graphql_url = "https://justyol.com/api/graphql"
            
            # Query for products
            query = {
                "query": f"""
                {{
                  collection(handle: "{collection}") {{
                    products(first: 250) {{
                      edges {{
                        node {{
                          id
                          title
                          handle
                          priceRange {{
                            minVariantPrice {{
                              amount
                              currencyCode
                            }}
                          }}
                          images(first: 1) {{
                            edges {{
                              node {{
                                originalSrc
                              }}
                            }}
                          }}
                        }}
                      }}
                    }}
                  }}
                }}
                """
            }
            
            logger.info(f"Trying GraphQL approach")
            response = requests.post(graphql_url, headers=graphql_headers, json=query, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'collection' in data['data'] and 'products' in data['data']['collection']:
                    products = []
                    for edge in data['data']['collection']['products']['edges']:
                        node = edge['node']
                        product = {
                            'id': node['id'],
                            'name': node['title'],
                            'url': f"https://justyol.com/en/products/{node['handle']}",
                            'price': f"{node['priceRange']['minVariantPrice']['amount']} {node['priceRange']['minVariantPrice']['currencyCode']}"
                        }
                        
                        if node['images']['edges']:
                            product['image'] = node['images']['edges'][0]['node']['originalSrc']
                        else:
                            product['image'] = 'N/A'
                            
                        products.append(product)
                    return products
            
            return None
        except Exception as e:
            logger.error(f"GraphQL approach failed: {str(e)}")
            return None
