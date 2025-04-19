"""
Functions for saving processed data to various output formats.
"""

import csv
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any


def save_to_csv(products: List[Dict[str, Any]], filename: str) -> str:
    """
    Save the products to a CSV file.
    
    Args:
        products: List of product dictionaries
        filename: Output filename
        
    Returns:
        Path to the saved file
    """
    file_path = Path(filename)
    
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        # Define the CSV columns
        fieldnames = ['name', 'brand', 'price', 'original_price', 'discount', 'url', 'image_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header and data
        writer.writeheader()
        for product in products:
            writer.writerow(product)
    
    return str(file_path.absolute())


def save_to_json(products: List[Dict[str, Any]], filename: str) -> str:
    """
    Save the products to a JSON file.
    
    Args:
        products: List of product dictionaries
        filename: Output filename
        
    Returns:
        Path to the saved file
    """
    file_path = Path(filename)
    
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(products, jsonfile, indent=2, ensure_ascii=False)
    
    return str(file_path.absolute())


def save_to_sqlite(products: List[Dict[str, Any]], db_file: str) -> str:
    """
    Save the products to a SQLite database.
    
    Args:
        products: List of product dictionaries
        db_file: SQLite database filename
        
    Returns:
        Path to the database file
    """
    file_path = Path(db_file)
    
    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()
    
    # Create the products table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        brand TEXT,
        price REAL,
        original_price REAL,
        discount INTEGER,
        url TEXT,
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Insert the products
    for product in products:
        cursor.execute(
            'INSERT INTO products (name, brand, price, original_price, discount, url, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (product.get('name'), product.get('brand'), product.get('price'), 
             product.get('original_price'), product.get('discount'), 
             product.get('url'), product.get('image_url'))
        )
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
    return str(file_path.absolute())
