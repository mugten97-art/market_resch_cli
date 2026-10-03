# reporter.py
"""
Module responsible for formatting output and generating client reports
both to console and structured JSON files.
"""

import json
from data_models import Product


def generate_report(all_products: list[Product], 
                    avg_prices: dict[str, float], 
                    top_products: list[Product], 
                    output_file: str = "report.json") -> None:
    """
    Outputs structured analytical results to the console and saves them to report.json.
    """
    report_data = {
        "total_products_analyzed": len(all_products),
        "average_price_per_category": avg_prices,
        "top_products": [p.to_dict() for p in top_products]
    }

    # Save output to report.json file
    with open(output_file, "w") as f:
        json.dump(report_data, f, indent=4)

    # Print clean summary to terminal console
    print("\n" + "=" * 45)
    print("          MARKET RESEARCH REPORT          ")
    print("=" * 45)
    print(f"Total Products Analyzed: {len(all_products)}")
    
    print("\n--- Average Price Per Category ---")
    for category, price in avg_prices.items():
        print(f"  * {category}: ${price:.2f}")
        
    print("\n--- Top Rated Products ---")
    for rank, product in enumerate(top_products, start=1):
        print(f"  {rank}. {product.name} ({product.category})")
        print(f"     Price: ${product.price:.2f} | Rating: {product.avg_score}/5.0 ({product.review_count} reviews)")
        
    print("=" * 45)
    print(f"[+] Full report successfully written to '{output_file}'\n")