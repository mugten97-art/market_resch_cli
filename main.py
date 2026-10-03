# main.py
"""
Main application entry point.
Supports multi-threading and asynchronous modes, CLI flags, and cProfile performance tracking.
"""

import argparse
import asyncio
import cProfile
import pstats
import sys
from concurrent.futures import ThreadPoolExecutor

import aiohttp
from config import API_BASE_URL, SCRAPER_BASE_URL, REQUEST_TIMEOUT
from api_fetcher import fetch_product_data
from scraper import scrape_review_data
from data_models import Product
from analyzer import (
    filter_products_with_reviews,
    calculate_avg_price_per_category,
    get_top_5_highest_rated
)
from reporter import generate_report


# --- MODE 1: MULTI-THREADING ---
def process_single_product_threaded(product_id: int) -> Product | None:
    raw_data = fetch_product_data(product_id)
    if not raw_data:
        return None
    avg_score, review_count = scrape_review_data(product_id)
    return Product(
        id=raw_data["id"],
        name=raw_data["name"],
        price=raw_data["price"],
        category=raw_data["category"],
        avg_score=avg_score,
        review_count=review_count
    )

def run_threaded_mode(product_ids: list[int]) -> list[Product]:
    print("[*] Running Mode 1: Multi-Threading (ThreadPoolExecutor)...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_single_product_threaded, product_ids))
    return [p for p in results if p is not None]


# --- MODE 2: ASYNCHRONOUS (asyncio + aiohttp) ---
async def fetch_async(session: aiohttp.ClientSession, url: str):
    try:
        async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
            if response.status == 200:
                return await response.json() if "api" in url else await response.text()
            return None
    except Exception:
        return None

async def process_single_product_async(session: aiohttp.ClientSession, product_id: int) -> Product | None:
    api_url = f"{API_BASE_URL}/{product_id}"
    review_url = f"{SCRAPER_BASE_URL}/{product_id}"
    
    api_data, review_html = await asyncio.gather(
        fetch_async(session, api_url),
        fetch_async(session, review_url)
    )
    
    if not api_data or not isinstance(api_data, dict):
        return None
        
    avg_score, review_count = 0.0, 0
    if review_html:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(review_html, "html.parser")
        score_el = soup.find("span", class_="rating")
        count_el = soup.find("span", class_="review-count")
        avg_score = float(score_el.text.strip()) if score_el else 0.0
        review_count = int(count_el.text.strip().replace(",", "")) if count_el else 0

    return Product(
        id=api_data["id"],
        name=api_data["name"],
        price=api_data["price"],
        category=api_data["category"],
        avg_score=avg_score,
        review_count=review_count
    )

async def run_async_mode(product_ids: list[int]) -> list[Product]:
    print("[*] Running Mode 2: Asynchronous (asyncio + aiohttp)...")
    async with aiohttp.ClientSession() as session:
        tasks = [process_single_product_async(session, pid) for pid in product_ids]
        results = await asyncio.gather(*tasks)
    return [p for p in results if p is not None]


# --- EXECUTION FLOW ---
def run_app():
    parser = argparse.ArgumentParser(description="Market Research CLI Aggregator")
    parser.add_argument("--mode", choices=["threads", "async"], required=True, help="Concurrency execution mode")
    parser.add_argument("--profile", action="store_true", help="Enable cProfile profiling")
    args = parser.parse_args()

    sample_product_ids = list(range(1, 21)) # IDs 1 through 20

    if args.mode == "threads":
        products = run_threaded_mode(sample_product_ids)
    else:
        products = asyncio.run(run_async_mode(sample_product_ids))

    # Process and Analyze
    valid_products = filter_products_with_reviews(products)
    avg_prices = calculate_avg_price_per_category(valid_products)
    top_products = get_top_5_highest_rated(valid_products)

    # Output Report
    generate_report(valid_products, avg_prices, top_products)


if __name__ == "__main__":
    if "--profile" in sys.argv:
        profiler = cProfile.Profile()
        profiler.enable()
        run_app()
        profiler.disable()
        
        print("\n--- PROFILER OUTPUT (Top Bottlenecks) ---")
        stats = pstats.Stats(profiler).sort_stats("cumtime")
        stats.print_stats(10)
    else:
        run_app()