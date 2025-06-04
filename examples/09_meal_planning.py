#!/usr/bin/env python3
"""
Example of meal planning using the USDA FDC API.

This script demonstrates how to use the recipe analysis functionality
to create and analyze a meal plan.
"""

import os
import json
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from usda_fdc import FdcClient
from usda_fdc.analysis.recipe import create_recipe, analyze_recipe
from usda_fdc.analysis.dri import DriType, Gender

# Path to the example data directory
DATA_DIR = Path(__file__).parent / "data"

def main():
    # Load API key from environment variable
    load_dotenv()
    api_key = os.getenv("FDC_API_KEY")
    
    if not api_key:
        print("Error: FDC_API_KEY environment variable not set.")
        return
    
    # Initialize the client
    client = FdcClient(api_key)
    
    print("=== Meal Planning Example ===")
    
    # Create breakfast recipe
    print("\nCreating breakfast recipe...")
    breakfast = create_recipe(
        name="Healthy Breakfast",
        ingredient_texts=[
            "1 cup oatmeal, cooked",
            "1 medium banana",
            "1 cup milk, 1% fat",
            "1 tbsp honey",
            "2 tbsp almonds, sliced"
        ],
        client=client,
        servings=1
    )
    
    # Analyze breakfast
    breakfast_analysis = analyze_recipe(
        breakfast,
        dri_type=DriType.RDA,
        gender=Gender.MALE,
        age=30
    )
    
    # Print breakfast analysis
    print(f"\nBreakfast: {breakfast.name}")
    print(f"Total Weight: {breakfast.total_weight_g:.1f}g")
    
    per_serving = breakfast_analysis.per_serving_analysis
    print(f"Calories: {per_serving.calories_per_serving:.1f} kcal")
    
    print("\nMacronutrient Distribution:")
    for macro, percent in per_serving.macronutrient_distribution.items():
        print(f"- {macro.capitalize()}: {percent:.1f}%")
    
    # Save breakfast DRI data for visualization
    breakfast_dri_data = {
        "recipe": {
            "name": breakfast.name,
            "servings": breakfast.servings,
            "ingredients": [
                {
                    "name": ingredient.description,
                    "amount": 1,  # Simplified for example
                    "unit": "serving",
                    "weight_g": ingredient.weight_g
                }
                for ingredient in breakfast.ingredients
            ]
        },
        "nutrition": {
            "calories": per_serving.calories_per_serving,
            "macronutrients": {
                "protein": per_serving.protein_per_serving,
                "carbs": per_serving.carbs_per_serving,
                "fat": per_serving.fat_per_serving,
                "fiber": per_serving.get_nutrient("fiber").amount if per_serving.get_nutrient("fiber") else 0
            },
            "macronutrient_distribution": per_serving.macronutrient_distribution,
            "dri_percentages": {}
        },
        "chart_data": {
            "nutrients": [],
            "percentages": [],
            "colors": [
                "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF",
                "#FF9F40", "#C9CBCF", "#7CFC00", "#00BFFF", "#FF7F50"
            ]
        }
    }
    
    # Add DRI percentages for key nutrients
    key_nutrients = [
        ("protein", "Protein"),
        ("fiber", "Fiber"),
        ("vitamin_a", "Vitamin A"),
        ("vitamin_c", "Vitamin C"),
        ("vitamin_d", "Vitamin D"),
        ("calcium", "Calcium"),
        ("iron", "Iron"),
        ("potassium", "Potassium"),
        ("magnesium", "Magnesium"),
        ("zinc", "Zinc")
    ]
    
    for nutrient_id, display_name in key_nutrients:
        nutrient_value = per_serving.get_nutrient(nutrient_id)
        if nutrient_value and nutrient_value.dri_percent is not None:
            breakfast_dri_data["nutrition"]["dri_percentages"][nutrient_id] = nutrient_value.dri_percent
            breakfast_dri_data["chart_data"]["nutrients"].append(display_name)
            breakfast_dri_data["chart_data"]["percentages"].append(nutrient_value.dri_percent)
    
    # Save the data to a file
    output_path = DATA_DIR / "breakfast_dri_chart.json"
    with open(output_path, 'w') as f:
        json.dump(breakfast_dri_data, f, indent=2)
    
    print(f"\nBreakfast DRI data saved to {output_path}")
    print("This data can be used for visualization in the visualization example.")
    
    # Create lunch recipe
    print("\nCreating lunch recipe...")
    lunch = create_recipe(
        name="Chicken Salad",
        ingredient_texts=[
            "3 oz grilled chicken breast",
            "2 cups mixed greens",
            "1/4 cup cherry tomatoes",
            "1/4 cup cucumber, sliced",
            "1 tbsp olive oil",
            "1 tbsp balsamic vinegar"
        ],
        client=client,
        servings=1
    )
    
    # Analyze lunch
    lunch_analysis = analyze_recipe(
        lunch,
        dri_type=DriType.RDA,
        gender=Gender.MALE,
        age=30
    )
    
    # Print lunch analysis
    print(f"\nLunch: {lunch.name}")
    print(f"Total Weight: {lunch.total_weight_g:.1f}g")
    
    per_serving = lunch_analysis.per_serving_analysis
    print(f"Calories: {per_serving.calories_per_serving:.1f} kcal")
    
    print("\nMacronutrient Distribution:")
    for macro, percent in per_serving.macronutrient_distribution.items():
        print(f"- {macro.capitalize()}: {percent:.1f}%")
    
    # Calculate daily totals
    print("\n=== Daily Totals (Breakfast + Lunch) ===")
    total_calories = (breakfast_analysis.per_serving_analysis.calories_per_serving + 
                     lunch_analysis.per_serving_analysis.calories_per_serving)
    total_protein = (breakfast_analysis.per_serving_analysis.protein_per_serving + 
                    lunch_analysis.per_serving_analysis.protein_per_serving)
    total_carbs = (breakfast_analysis.per_serving_analysis.carbs_per_serving + 
                  lunch_analysis.per_serving_analysis.carbs_per_serving)
    total_fat = (breakfast_analysis.per_serving_analysis.fat_per_serving + 
                lunch_analysis.per_serving_analysis.fat_per_serving)
    
    print(f"Total Calories: {total_calories:.1f} kcal")
    print(f"Total Protein: {total_protein:.1f} g")
    print(f"Total Carbs: {total_carbs:.1f} g")
    print(f"Total Fat: {total_fat:.1f} g")
    
    # Calculate macronutrient distribution
    protein_calories = total_protein * 4.0
    carbs_calories = total_carbs * 4.0
    fat_calories = total_fat * 9.0
    total_macro_calories = protein_calories + carbs_calories + fat_calories
    
    print("\nMacronutrient Distribution:")
    print(f"- Protein: {(protein_calories / total_macro_calories * 100):.1f}%")
    print(f"- Carbs: {(carbs_calories / total_macro_calories * 100):.1f}%")
    print(f"- Fat: {(fat_calories / total_macro_calories * 100):.1f}%")

if __name__ == "__main__":
    main()