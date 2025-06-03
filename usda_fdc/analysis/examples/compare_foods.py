"""
Example script for comparing foods.
"""

import os
from dotenv import load_dotenv

from usda_fdc import FdcClient
from usda_fdc.analysis import compare_foods


def main():
    """Main function."""
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("FDC_API_KEY")
    
    if not api_key:
        print("Error: FDC_API_KEY environment variable not set.")
        return
    
    # Initialize the client
    client = FdcClient(api_key)
    
    # Define foods to compare
    # Apple, raw, with skin
    # Banana, raw
    # Orange, raw, all commercial varieties
    fdc_ids = [1750340, 1750341, 1750342]
    
    # Get the foods
    foods = [client.get_food(fdc_id) for fdc_id in fdc_ids]
    
    # Compare the foods
    comparison = compare_foods(
        foods,
        nutrient_ids=["vitamin_c", "potassium", "fiber", "sugar"],
        serving_sizes=[100.0, 100.0, 100.0]
    )
    
    # Print comparison
    print("Nutrient Comparison (per 100g)")
    print()
    
    for nutrient_id, values in comparison.items():
        if not values:
            continue
        
        # Get the nutrient name and unit from the first value
        _, _, unit = values[0]
        
        print(f"{nutrient_id.capitalize()}:")
        for food, amount, _ in values:
            print(f"  {food}: {amount:.1f} {unit}")
        print()


if __name__ == "__main__":
    main()