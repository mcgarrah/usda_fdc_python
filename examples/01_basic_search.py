#!/usr/bin/env python3
"""
Basic example of searching for foods using the USDA FDC API.
"""

import os
from dotenv import load_dotenv
from usda_fdc import FdcClient

def main():
    # Load API key from environment variable
    load_dotenv()
    api_key = os.getenv("FDC_API_KEY")
    
    if not api_key:
        print("Error: FDC_API_KEY environment variable not set.")
        print("Please set it or pass your API key directly to FdcClient.")
        return
    
    # Initialize the client
    client = FdcClient(api_key)
    
    # Search for foods containing "apple"
    print("Searching for 'apple'...")
    results = client.search("apple", page_size=5)
    
    # Print search results
    print(f"Found {results.total_hits} results (showing first 5)")
    print(f"Page {results.current_page} of {results.total_pages}")
    print("\nResults:")
    
    for food in results.foods:
        print(f"- {food.description} (FDC ID: {food.fdc_id}, Type: {food.data_type})")
    
    # Search with data type filter
    print("\nSearching for branded apples only...")
    branded_results = client.search("apple", data_type=["Branded"], page_size=5)
    
    print(f"Found {branded_results.total_hits} branded results (showing first 5)")
    for food in branded_results.foods:
        print(f"- {food.description} (Brand: {food.brand_name})")

if __name__ == "__main__":
    main()