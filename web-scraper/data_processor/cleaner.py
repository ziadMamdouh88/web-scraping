"""
Functions for cleaning and processing scraped data.
"""

import re
from typing import List, Dict, Any, Union


def clean_product_data(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean and process the scraped product data.
    
    Args:
        products: List of standardized product dictionaries
        
    Returns:
        List of cleaned product dictionaries
    """
    cleaned_products = []
    
    for product in products:
        cleaned_product = {
            'name': clean_name(product.get('name')),
            'brand': product.get('brand'),
            'price': clean_price(product.get('price')),
            'original_price': clean_price(product.get('original_price')),
            'discount': clean_discount(product.get('discount')),
            'url': product.get('url'),
            'image_url': product.get('image_url')
        }
        cleaned_products.append(cleaned_product)
    
    return cleaned_products


def clean_name(name: str) -> str:
    """
    Clean the product name.
    
    Args:
        name: Raw product name
        
    Returns:
        Cleaned product name
    """
    if not name:
        return None
    
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name


def clean_price(price: str) -> float:
    """
    Clean the price and convert to float.
    
    Args:
        price: Raw price string (e.g., "152 dh")
        
    Returns:
        Price as a float
    """
    if not price:
        return None
    
    # Extract numeric part from price string
    match = re.search(r'(\d+(?:\.\d+)?)', str(price))
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    
    return None


def clean_discount(discount: str) -> int:
    """
    Clean the discount percentage and convert to integer.
    
    Args:
        discount: Raw discount string (e.g., "-50%")
        
    Returns:
        Discount as an integer
    """
    if not discount:
        return None
    
    # Extract numeric part from discount string
    match = re.search(r'-?(\d+)%?', str(discount))
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    
    return None
