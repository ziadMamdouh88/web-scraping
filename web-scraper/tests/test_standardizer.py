"""
Unit tests for the data standardization functions.
"""

import unittest
from data_processor.standardizer import standardize_products


class TestStandardizer(unittest.TestCase):
    """Test cases for data standardization functions."""
    
    def test_standardize_products(self):
        """Test the standardize_products function."""
        # Test products from different sources
        test_products = [
            # API format
            {
                'title': 'Test Product 1',
                'vendor': 'JustYol',
                'price_min': 99.99,
                'handle': 'test-product-1',
                'images': [{'src': 'https://example.com/image1.jpg'}]
            },
            # Selenium format
            {
                'name': 'Test Product 2',
                'brand': 'JWomen',
                'price': '199.99 dh',
                'original_price': '299.99 dh',
                'discount': '-33%',
                'url': 'https://justyol.com/en/products/test-product-2',
                'image_url': 'https://example.com/image2.jpg'
            },
            # Playwright format
            {
                'name': 'Test Product 3',
                'brand': 'JKids',
                'price': '50 dh',
                'original_price': '100 dh',
                'discount': '-50%',
                'url': 'https://justyol.com/en/products/test-product-3',
                'image': 'https://example.com/image3.jpg'
            }
        ]
        
        standardized = standardize_products(test_products)
        
        # Check that we have the correct number of products
        self.assertEqual(len(standardized), 3)
        
        # Check that the data is standardized correctly
        self.assertEqual(standardized[0]['name'], 'Test Product 1')
        self.assertEqual(standardized[0]['brand'], 'JustYol')
        self.assertEqual(standardized[0]['price'], '99.99')
        self.assertEqual(standardized[0]['url'], 'https://justyol.com/en/products/test-product-1')
        self.assertEqual(standardized[0]['image_url'], 'https://example.com/image1.jpg')
        
        self.assertEqual(standardized[1]['name'], 'Test Product 2')
        self.assertEqual(standardized[1]['brand'], 'JWomen')
        self.assertEqual(standardized[1]['price'], '199.99 dh')
        self.assertEqual(standardized[1]['original_price'], '299.99 dh')
        self.assertEqual(standardized[1]['discount'], '-33%')
        self.assertEqual(standardized[1]['url'], 'https://justyol.com/en/products/test-product-2')
        self.assertEqual(standardized[1]['image_url'], 'https://example.com/image2.jpg')
        
        self.assertEqual(standardized[2]['name'], 'Test Product 3')
        self.assertEqual(standardized[2]['brand'], 'JKids')
        self.assertEqual(standardized[2]['price'], '50 dh')
        self.assertEqual(standardized[2]['original_price'], '100 dh')
        self.assertEqual(standardized[2]['discount'], '-50%')
        self.assertEqual(standardized[2]['url'], 'https://justyol.com/en/products/test-product-3')
        self.assertEqual(standardized[2]['image_url'], 'https://example.com/image3.jpg')


if __name__ == "__main__":
    unittest.main()
