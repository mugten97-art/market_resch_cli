 # api_fetcher.py
"""
Module responsible for interacting with the RESTful API to fetch product details.
Includes LRU caching and robust exception handling.
"""

import requests
from functools import lru_cache
from config import API_BASE_URL, REQUEST_TIMEOUT


@lru_cache(maxsize=128)
def fetch_product_data(product_id: int) -> dict | None:
    """
    Fetches product details from the REST API for a given product ID.
    
    Uses functools.lru_cache to store previously retrieved responses in memory.
    
    Args:
        product_id (int): The unique identifier for the product.
        
    Returns:
        dict: Product details containing ID, Name, Price, and Category if successful.
        None: If the request fails or encounters an error.
    """
    url = f"{API_BASE_URL}/{product_id}"
    
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        
        # Raise HTTPError if status code is 4xx or 5xx
        response.raise_for_status()
        
        # Parse and return JSON payload
        data = response.json()
        return data

    except requests.exceptions.Timeout:
        print(f"[API Warning] Request timed out for Product ID {product_id}.")
    except requests.exceptions.HTTPError as http_err:
        print(f"[API Error] HTTP error {response.status_code} for Product ID {product_id}: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"[API Error] Connection error for Product ID {product_id}: {req_err}")
    except ValueError:
        print(f"[API Error] Failed to decode JSON response for Product ID {product_id}.")
        
    return None


def fetch_all_products_sync(product_ids: list[int]) -> list[dict]:
    """
    Helper function to sequentially fetch multiple products (standard synchronous flow).
    """
    products = []
    for pid in product_ids:
        data = fetch_product_data(pid)
        if data:
            products.append(data)
    return products