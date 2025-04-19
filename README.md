# web-scraping# JustYol Web Scraping & Data Processing

## Overview
This project implements a comprehensive web scraping solution for JustYol's e-commerce website. It uses multiple approaches to extract product data, with automatic fallbacks if one method fails. The extracted data is processed, standardized, and output in multiple formats (CSV, JSON, and SQLite database).

## Features
- **Multiple Data Extraction Methods**:
  - Direct API access
  - Inventory API access
  - GraphQL queries
  - Network request monitoring with Selenium
  - HTML scraping with Playwright as fallback
- **Data Processing**:
  - Standardization of data from different sources
  - Cleaning and type conversion
  - Multiple output formats
- **API Access**:
  - FastAPI implementation to serve the scraped data
  - Filtering by brand
  - Pagination support

## Setup
1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
### Scraping Data
```bash
python scrape.py [options]
```

#### Options
- `--url`: The URL to scrape (default: "https://justyol.com/en/collections/women-handbags")
- `--pages`: Number of pages to scrape (default: 2)
- `--output`: Output format(s), comma-separated (default: "csv,json")
- `--db`: SQLite database file (default: "products.db")
- `--method`: Scraping method to use (default: "auto", options: "api", "selenium", "playwright", "auto")

### Examples
```bash
# Use all methods with automatic fallback
python scrape.py

# Specify a particular method
python scrape.py --method=api

# Scrape more pages
python scrape.py --pages=5

# Save only to database
python scrape.py --output=db
```

### Running the API Server
First, make sure you've scraped some data to create the database:
```bash
python scrape.py --output=db
```

Then start the API server:
```bash
uvicorn api.main:app --reload
```

The API will be available at http://localhost:8000 with documentation at http://localhost:8000/docs

### API Endpoints
- `GET /products`: Get all products with optional filtering and pagination
- `GET /products/{product_id}`: Get a specific product by ID
- `GET /brands`: Get a list of all brands

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_justyol_cleaner.py
pytest tests/test_standardizer.py
```

## Project Structure
```
├── scrape.py                 # Main entry point
├── scraper/                  # Scraping implementations
│   ├── base.py               # Abstract base scraper class
│   ├── api_scraper.py        # API-based scraping methods
│   ├── selenium_scraper.py   # Selenium-based scraping
│   └── justyol.py            # Playwright-based scraping
├── data_processor/           # Data processing
│   ├── cleaner.py            # Data cleaning functions
│   ├── standardizer.py       # Data standardization
│   └── output.py             # Output formatting
├── api/                      # API implementation
│   └── main.py               # FastAPI implementation
└── tests/                    # Unit tests
    ├── test_justyol_cleaner.py
    └── test_standardizer.py
```

## Notes
- The scraper respects robots.txt and includes delays between requests
- Multiple scraping methods provide redundancy in case one approach fails
- The API server requires the database to be created first by running the scraper

## Future Improvements
- Add proxy rotation for better anonymity
- Implement more advanced error recovery mechanisms
- Add support for more e-commerce platforms
- Enhance the API with filtering and pagination
- Implement a caching layer to reduce redundant requests
