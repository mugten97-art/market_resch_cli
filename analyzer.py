# analyzer.py
"""
Module responsible for data processing and analysis using functional programming
constructs (map, filter, reduce).
"""

from functools import reduce
from data_models import Product


def filter_products_with_reviews(products: list[Product]) -> list[Product]:
    """
    Uses filter() to remove products that have no reviews (review_count == 0).
    """
    return list(filter(lambda p: p.review_count > 0, products))


def calculate_avg_price_per_category(products: list[Product]) -> dict[str, float]:
    """
    Calculates average price per category using filter and reduce.
    """
    # Extract unique categories using map and set
    categories = list(set(map(lambda p: p.category, products)))
    category_averages = {}

    for category in categories:
        # Filter products belonging to current category
        cat_products = list(filter(lambda p: p.category == category, products))
        
        if cat_products:
            # Sum total price using reduce
            total_price = reduce(lambda acc, p: acc + p.price, cat_products, 0.0)
            avg_price = total_price / len(cat_products)
            category_averages[category] = round(avg_price, 2)

    return category_averages


def get_top_5_highest_rated(products: list[Product]) -> list[Product]:
    """
    Finds the top 5 highest-rated products based on avg_score.
    """
    sorted_products = sorted(products, key=lambda p: p.avg_score, reverse=True)
    return sorted_products[:5]