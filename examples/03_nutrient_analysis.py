#!/usr/bin/env python3
"""
Example of analyzing nutrient content using the USDA FDC API.
"""

import os
from dotenv import load_dotenv
from usda_fdc import FdcClient
from usda_fdc.analysis import analyze_food, DriType, Gender

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
    food = client.get_food(fdc_id)
    
    # Analyze the food
    print(f"Analyzing nutrient content for {food.description}...")
    analysis = analyze_food(
        food,
        dri_type=DriType.RDA,
        gender=Gender.MALE,
        serving_size=100.0  # 100g serving
    )
    
    # Print basic analysis information
    print(f"\nServing Size: {analysis.serving_size}g")
    print(f"Calories: {analysis.calories_per_serving:.1f} kcal")
    
    # Print macronutrient distribution
    print("\nMacronutrient Distribution:")
    for macro, percent in analysis.macronutrient_distribution.items():
        print(f"- {macro.capitalize()}: {percent:.1f}%")
    
    # Print key nutrients with DRI percentages
    print("\nKey Nutrients:")
    for nutrient_id in ["protein", "fiber", "vitamin_c", "calcium", "iron"]:
        nutrient_value = analysis.get_nutrient(nutrient_id)
        if nutrient_value:
            dri_percent = f"{nutrient_value.dri_percent:.1f}%" if nutrient_value.dri_percent is not None else "N/A"
            print(f"- {nutrient_value.nutrient.display_name}: {nutrient_value.amount:.1f} {nutrient_value.unit} ({dri_percent} of DRI)")
    
    # Compare with female DRI values
    print("\nComparing with female DRI values...")
    female_analysis = analyze_food(
        food,
        dri_type=DriType.RDA,
        gender=Gender.FEMALE,
        serving_size=100.0
    )
    
    print("\nKey Nutrients (Female DRI):")
    for nutrient_id in ["iron", "calcium"]:
        nutrient_value = female_analysis.get_nutrient(nutrient_id)
        if nutrient_value:
            dri_percent = f"{nutrient_value.dri_percent:.1f}%" if nutrient_value.dri_percent is not None else "N/A"
            print(f"- {nutrient_value.nutrient.display_name}: {nutrient_value.amount:.1f} {nutrient_value.unit} ({dri_percent} of DRI)")

if __name__ == "__main__":
    main()