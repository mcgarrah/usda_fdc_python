#!/usr/bin/env python3
"""
Example of comparing multiple foods using the USDA FDC API.
"""

import os
from dotenv import load_dotenv
from usda_fdc import FdcClient
from usda_fdc.analysis import compare_foods

def main():
    # Load API key from environment variable
    load_dotenv()
    api_key = os.getenv("FDC_API_KEY")
    
    if not api_key:
        print("Error: FDC_API_KEY environment variable not set.")
        return
    
    # Initialize the client
    client = FdcClient(api_key)
    
    # Get foods to compare
    print("Getting foods to compare...")
    foods = [
        client.get_food(1750340),  # Apple, raw, with skin
        client.get_food(1750341),  # Banana, raw
        client.get_food(1750342)   # Orange, raw, all commercial varieties
    ]
    
    print(f"Comparing: {', '.join(food.description for food in foods)}")
    
    # Compare the foods
    comparison = compare_foods(
        foods,
        nutrient_ids=["vitamin_c", "potassium", "fiber", "sugar"],
        serving_sizes=[100.0, 100.0, 100.0]  # 100g serving for each
    )
    
    # Print the comparison
    print("\nNutrient Comparison (per 100g):")
    for nutrient_id, values in comparison.items():
        if not values:
            continue
        
        # Get the nutrient name and unit from the first value
        _, _, unit = values[0]
        
        print(f"\n{nutrient_id.capitalize()}:")
        for food, amount, _ in values:
            print(f"- {food}: {amount:.1f} {unit}")
    
    # Compare with different serving sizes
    print("\nComparing with typical serving sizes:")
    comparison = compare_foods(
        foods,
        nutrient_ids=["vitamin_c", "potassium", "fiber", "sugar"],
        serving_sizes=[182.0, 118.0, 131.0]  # Medium apple, medium banana, medium orange
    )
    
    print("\nNutrient Comparison (per typical serving):")
    for nutrient_id, values in comparison.items():
        if not values:
            continue
        
        # Get the nutrient name and unit from the first value
        _, _, unit = values[0]
        
        print(f"\n{nutrient_id.capitalize()}:")
        for food, amount, _ in values:
            print(f"- {food}: {amount:.1f} {unit}")

if __name__ == "__main__":
    main()