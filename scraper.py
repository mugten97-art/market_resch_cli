# scraper.py
"""
Module responsible for web scraping public sentiment data (review scores and review counts)
from simulated static web pages using BeautifulSoup.
"""

import requests
from bs4 import BeautifulSoup
from config import SCRAPER_BASE_URL, REQUEST_TIMEOUT


def scrape_review_data(product_id: int) -> tuple[float, int]:
    """
    Scrapes the review page for a given product ID to extract average review score
    and total review count.
    
    Args:
        product_id (int): The unique identifier for the product.
        
    Returns:
        tuple[float, int]: A tuple containing (avg_score, review_count).
                           Returns (0.0, 0) if the page does not exist or fails.
    """
    url = f"{SCRAPER_BASE_URL}/{product_id}"
    
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        
        # Handle case where product review page does not exist (e.g., HTTP 404)
        if response.status_code == 404:
            print(f"[Scraper Info] Review page not found for Product ID {product_id}. Assigning zero reviews.")
            return 0.0, 0
            
        response.raise_for_status()
        
        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find rating and review count elements (adjust class names according to mock HTML)
        score_element = soup.find("span", class_="rating") or soup.find("div", class_="rating")
        count_element = soup.find("span", class_="review-count") or soup.find("div", class_="review-count")
        
        # Extract numerical values safely
        avg_score = float(score_element.text.strip()) if score_element else 0.0
        review_count = int(count_element.text.strip().replace(",", "")) if count_element else 0
        
        return avg_score, review_count

    except requests.exceptions.RequestException as e:
        print(f"[Scraper Error] Network issue while scraping Product ID {product_id}: {e}")
        return 0.0, 0
    except (ValueError, AttributeError) as e:
        print(f"[Scraper Error] Parsing failure for Product ID {product_id}: {e}")
        return 0.0, 0