# config.py
"""
Configuration settings and constants for the market resch CLI application.
"""
#Base URLs for API fetching and Web Scraping
#(Replace these with actual test URLs provided by your instructor or your local mock server)
API_BASE_URL = "http://localhost:5000/api/products"
SCRAPER_BASE_URL = "http://localhost:5000/reviews"

#Network Request Settings
REQUEST_TIMEOUT = 5 # Timeout in seconds for HTTP requests
MAX_RETRIES = 3           # Maximum retry attempts for failed requests