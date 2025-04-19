"""
Unit tests for the data cleaning functions specific to JustYol data.
"""

import unittest
from data_processor.cleaner import clean_name, clean_price, clean_discount


class TestJustYolCleaner(unittest.TestCase):
    """Test cases for JustYol data cleaning functions."""
    
    def test_clean_name(self):
        """Test the clean_name function."""
        # Test normal name
        self.assertEqual(clean_name("Simple Siyah Kol Çantası"), "Simple Siyah Kol Çantası")
        
        # Test name with extra whitespace
        self.assertEqual(clean_name("  Simple   Siyah  Kol  Çantası  "), "Simple Siyah Kol Çantası")
        
        # Test None input
        self.assertIsNone(clean_name(None))
    
    def test_clean_price(self):
        """Test the clean_price function."""
        # Test normal price
        self.assertEqual(clean_price("152 dh"), 152.0)
        
        # Test price with decimal
        self.assertEqual(clean_price("152.99 dh"), 152.99)
        
        # Test None input
        self.assertIsNone(clean_price(None))
        
        # Test invalid price
        self.assertIsNone(clean_price("Price not available"))
    
    def test_clean_discount(self):
        """Test the clean_discount function."""
        # Test normal discount
        self.assertEqual(clean_discount("-50%"), 50)
        
        # Test discount without percentage sign
        self.assertEqual(clean_discount("-50"), 50)
        
        # Test None input
        self.assertIsNone(clean_discount(None))
        
        # Test invalid discount
        self.assertIsNone(clean_discount("Sale"))


if __name__ == "__main__":
    unittest.main()
