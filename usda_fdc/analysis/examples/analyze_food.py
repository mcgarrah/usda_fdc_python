"""
Example script for analyzing a food.
"""

import os
import json
from dotenv import load_dotenv

from usda_fdc import FdcClient
from usda_fdc.analysis import analyze_food, DriType, Gender
from usda_fdc.analysis.visualization import generate_html_report


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
    
    # Get a food (Apple, raw, with skin)
    food = client.get_food(1750340)
    
    # Analyze the food
    analysis = analyze_food(
        food,
        dri_type=DriType.RDA,
        gender=Gender.MALE,
        serving_size=100.0
    )
    
    # Print basic information
    print(f"Nutrient Analysis for {food.description}")
    print(f"FDC ID: {food.fdc_id}")
    print(f"Data Type: {food.data_type}")
    print(f"Serving Size: 100g")
    print(f"Calories: {analysis.calories_per_serving:.1f} kcal")
    print()
    
    # Print macronutrient distribution
    print("Macronutrient Distribution:")
    for macro, percent in analysis.macronutrient_distribution.items():
        print(f"  {macro.capitalize()}: {percent:.1f}%")
    print()
    
    # Print nutrients
    print("Nutrients:")
    for group_name, group_nutrients in [
        ("Macronutrients", ["protein", "fat", "carbohydrate", "fiber"]),
        ("Vitamins", [n for n in analysis.nutrients if analysis.nutrients[n].nutrient.group == "vitamin"]),
        ("Minerals", [n for n in analysis.nutrients if analysis.nutrients[n].nutrient.group == "mineral"])
    ]:
        print(f"\n{group_name}:")
        for nutrient_id in group_nutrients:
            nutrient_value = analysis.get_nutrient(nutrient_id)
            if nutrient_value:
                dri_percent = f"{nutrient_value.dri_percent:.1f}%" if nutrient_value.dri_percent is not None else "N/A"
                print(f"  {nutrient_value.nutrient.display_name}: {nutrient_value.amount:.1f} {nutrient_value.unit} ({dri_percent} of DRI)")
    
    # Generate an HTML report
    html = generate_html_report(analysis)
    with open("apple_analysis.html", "w") as f:
        f.write(html)
    print("\nHTML report saved to apple_analysis.html")


if __name__ == "__main__":
    main()