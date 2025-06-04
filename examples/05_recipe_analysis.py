#!/usr/bin/env python3
"""
Example of analyzing a recipe using the USDA FDC API.
"""

import os
from dotenv import load_dotenv
from usda_fdc import FdcClient
from usda_fdc.analysis import DriType, Gender
from usda_fdc.analysis.recipe import create_recipe, analyze_recipe

def main():
    # Load API key from environment variable
    load_dotenv()
    api_key = os.getenv("FDC_API_KEY")
    
    if not api_key:
        print("Error: FDC_API_KEY environment variable not set.")
        return
    
    # Initialize the client
    client = FdcClient(api_key)
    
    # Define a recipe
    recipe_name = "Fruit Salad"
    ingredient_texts = [
        "1 apple",
        "1 banana",
        "100g strawberries",
        "50g blueberries",
        "1 tbsp honey"
    ]
    
    print(f"Creating recipe: {recipe_name}")
    print("Ingredients:")
    for ingredient in ingredient_texts:
        print(f"- {ingredient}")
    
    # Create the recipe
    recipe = create_recipe(
        name=recipe_name,
        ingredient_texts=ingredient_texts,
        client=client,
        servings=2
    )
    
    # Print recipe information
    print(f"\nRecipe created with {len(recipe.ingredients)} ingredients")
    print(f"Total weight: {recipe.total_weight_g:.1f}g")
    print(f"Weight per serving: {recipe.get_weight_per_serving():.1f}g")
    
    # Analyze the recipe
    print("\nAnalyzing recipe...")
    analysis = analyze_recipe(
        recipe,
        dri_type=DriType.RDA,
        gender=Gender.MALE
    )
    
    # Print nutrition information per serving
    print("\nNutrition per serving:")
    per_serving = analysis.per_serving_analysis
    print(f"Calories: {per_serving.calories_per_serving:.1f} kcal")
    
    # Print macronutrient distribution
    print("\nMacronutrient Distribution:")
    for macro, percent in per_serving.macronutrient_distribution.items():
        print(f"- {macro.capitalize()}: {percent:.1f}%")
    
    # Print key nutrients
    print("\nKey Nutrients per serving:")
    for nutrient_id in ["protein", "fiber", "vitamin_c", "potassium"]:
        nutrient_value = per_serving.get_nutrient(nutrient_id)
        if nutrient_value:
            dri_percent = f"{nutrient_value.dri_percent:.1f}%" if nutrient_value.dri_percent is not None else "N/A"
            print(f"- {nutrient_value.nutrient.name}: {nutrient_value.amount:.1f} {nutrient_value.unit} ({dri_percent} of DRI)")
    
    # Print ingredient breakdown
    print("\nIngredient breakdown:")
    for i, (ingredient, analysis) in enumerate(zip(recipe.ingredients, analysis.ingredient_analyses)):
        print(f"\n{i+1}. {ingredient.food.description} ({ingredient.weight_g:.1f}g):")
        print(f"   Calories: {analysis.calories_per_serving:.1f} kcal")
        
        # Get vitamin C content if available
        vit_c = analysis.get_nutrient("vitamin_c")
        if vit_c:
            print(f"   Vitamin C: {vit_c.amount:.1f} {vit_c.unit}")

if __name__ == "__main__":
    main()