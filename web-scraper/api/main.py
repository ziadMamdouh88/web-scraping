"""
Simple FastAPI implementation to serve the scraped data.
"""

import sqlite3
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="JustYol Product API",
    description="API for accessing scraped JustYol product data",
    version="1.0.0"
)

class Product(BaseModel):
    """Product model for API responses."""
    id: Optional[int] = None
    name: str
    brand: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    discount: Optional[int] = None
    url: Optional[str] = None
    image_url: Optional[str] = None


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint that returns API information."""
    return {
        "message": "JustYol Product API",
        "version": "1.0.0",
        "endpoints": [
            "/products",
            "/products/{product_id}",
            "/brands"
        ]
    }


@app.get("/products", response_model=List[Product], tags=["Products"])
async def get_products(limit: int = 100, offset: int = 0, brand: Optional[str] = None):
    """
    Get a list of products.
    
    Args:
        limit: Maximum number of products to return
        offset: Number of products to skip
        brand: Filter products by brand
        
    Returns:
        List of products
    """
    try:
        # Connect to the database
        conn = sqlite3.connect("products.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build the query
        query = "SELECT id, name, brand, price, original_price, discount, url, image_url FROM products"
        params = []
        
        # Add brand filter if provided
        if brand:
            query += " WHERE brand = ?"
            params.append(brand)
        
        # Add limit and offset
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # Execute the query
        cursor.execute(query, params)
        
        # Convert the results to a list of dictionaries
        products = [dict(row) for row in cursor.fetchall()]
        
        # Close the connection
        conn.close()
        
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products/{product_id}", response_model=Product, tags=["Products"])
async def get_product(product_id: int):
    """
    Get a specific product by ID.
    
    Args:
        product_id: The ID of the product to retrieve
        
    Returns:
        Product details
    """
    try:
        # Connect to the database
        conn = sqlite3.connect("products.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query the product
        cursor.execute(
            "SELECT id, name, brand, price, original_price, discount, url, image_url FROM products WHERE id = ?",
            (product_id,)
        )
        
        # Get the result
        product = cursor.fetchone()
        
        # Close the connection
        conn.close()
        
        if product:
            return dict(product)
        else:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/brands", tags=["Brands"])
async def get_brands():
    """
    Get a list of all brands.
    
    Returns:
        List of unique brands
    """
    try:
        # Connect to the database
        conn = sqlite3.connect("products.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query the brands
        cursor.execute("SELECT DISTINCT brand FROM products WHERE brand IS NOT NULL")
        
        # Get the results
        brands = [row['brand'] for row in cursor.fetchall()]
        
        # Close the connection
        conn.close()
        
        return {"brands": brands}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
