"""
Functions for standardizing product data from different sources.
"""

from typing import List, Dict, Any


def standardize_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Standardize product data to ensure consistent format.
    
    Args:
        products: List of raw product dictionaries from various sources
        
    Returns:
        List of standardized product dictionaries
    """
    standardized = []
    
    for product in products:
        std_product = {}
        
        # Handle different formats of product data
        if isinstance(product, dict):
            # Extract name
            if 'name' in product:
                std_product['name'] = product['name']
            elif 'title' in product:
                std_product['name'] = product['title']
            else:
                std_product['name'] = 'Unknown Product'
                
            # Extract brand
            if 'brand' in product:
                std_product['brand'] = product['brand']
            elif 'vendor' in product:
                std_product['brand'] = product['vendor']
            else:
                std_product['brand'] = None
                
            # Extract price
            if 'price' in product:
                std_product['price'] = product['price']
            elif 'price_min' in product:
                std_product['price'] = str(product['price_min'])
            elif 'variants' in product and product['variants'] and 'price' in product['variants'][0]:
                std_product['price'] = product['variants'][0]['price']
            else:
                std_product['price'] = None
                
            # Extract original price
            if 'original_price' in product:
                std_product['original_price'] = product['original_price']
            elif 'compare_at_price' in product:
                std_product['original_price'] = product['compare_at_price']
            elif 'variants' in product and product['variants'] and 'compare_at_price' in product['variants'][0]:
                std_product['original_price'] = product['variants'][0]['compare_at_price']
            else:
                std_product['original_price'] = std_product['price']
                
            # Extract discount
            if 'discount' in product:
                std_product['discount'] = product['discount']
            else:
                std_product['discount'] = None
                
            # Extract URL
            if 'url' in product:
                std_product['url'] = product['url']
            elif 'handle' in product:
                std_product['url'] = f"https://justyol.com/en/products/{product['handle']}"
            else:
                std_product['url'] = None
                
            # Extract image URL
            if 'image_url' in product:
                std_product['image_url'] = product['image_url']
            elif 'image' in product:
                if isinstance(product['image'], str):
                    std_product['image_url'] = product['image']
                elif isinstance(product['image'], dict) and 'src' in product['image']:
                    std_product['image_url'] = product['image']['src']
            elif 'featured_image' in product:
                std_product['image_url'] = product['featured_image']
            elif 'images' in product and product['images']:
                if isinstance(product['images'], list) and product['images']:
                    img = product['images'][0]
                    if isinstance(img, dict) and 'src' in img:
                        std_product['image_url'] = img['src']
                    else:
                        std_product['image_url'] = str(img)
                else:
                    std_product['image_url'] = str(product['images'])
            else:
                std_product['image_url'] = None
                
            # Only add products with at least a name
            if std_product['name'] and std_product['name'] != 'Unknown Product':
                standardized.append(std_product)
            
    return standardized
