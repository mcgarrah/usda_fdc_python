#!/usr/bin/env python3
"""
Example of retrieving detailed food information from the USDA FDC API.
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
        return
    
    # Initialize the client
    client = FdcClient(api_key)
    
    # Get food by FDC ID (Apple, raw, with skin)
    fdc_id = 1750340
    print(f"Getting food details for FDC ID: {fdc_id}")
    
    food = client.get_food(fdc_id)
    
    # Print basic food information
    print(f"\nFood: {food.description}")
    print(f"FDC ID: {food.fdc_id}")
    print(f"Data Type: {food.data_type}")
    print(f"Publication Date: {food.publication_date}")
    
    # Print nutrient information
    print("\nNutrient Information (top 10):")
    for i, nutrient in enumerate(food.nutrients[:10]):
        print(f"- {nutrient.name}: {nutrient.amount} {nutrient.unit_name}")
    
    print(f"\nTotal nutrients: {len(food.nutrients)}")
    
    # Print portion information
    if food.food_portions:
        print("\nPortion Information:")
        for portion in food.food_portions:
            print(f"- {portion.amount} {portion.measure_unit}: {portion.gram_weight}g")
    
    # Get multiple foods at once
    print("\nGetting multiple foods at once...")
    foods = client.get_foods([1750340, 1750341, 1750342])  # Apple, Banana, Orange
    
    print("\nRetrieved foods:")
    for food in foods:
        print(f"- {food.description} (FDC ID: {food.fdc_id})")

if __name__ == "__main__":
    main()