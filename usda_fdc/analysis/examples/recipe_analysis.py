"""
Example script for analyzing a recipe.
"""

import os
from dotenv import load_dotenv

from usda_fdc import FdcClient
from usda_fdc.analysis import DriType, Gender
from usda_fdc.analysis.recipe import create_recipe, analyze_recipe


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
    
    # Define a recipe
    recipe_name = "Fruit Salad"
    ingredient_texts = [
        "1 apple",
        "1 banana",
        "100g strawberries",
        "50g blueberries",
        "1 tbsp honey"
    ]
    
    # Create the recipe
    recipe = create_recipe(
        name=recipe_name,
        ingredient_texts=ingredient_texts,
        client=client,
        servings=2
    )
    
    # Analyze the recipe
    analysis = analyze_recipe(
        recipe,
        dri_type=DriType.RDA,
        gender=Gender.MALE
    )
    
    # Print recipe information
    print(f"Recipe Analysis for {recipe.name}")
    print(f"Servings: {recipe.servings}")
    print(f"Total Weight: {recipe.total_weight_g:.1f}g")
    print(f"Weight per Serving: {recipe.get_weight_per_serving():.1f}g")
    print()
    
    # Print ingredients
    print("Ingredients:")
    for ingredient in recipe.ingredients:
        print(f"  {ingredient.amount} {ingredient.unit} {ingredient.food.description} ({ingredient.weight_g:.1f}g)")
    print()
    
    # Print nutrition per serving
    print("Nutrition per Serving:")
    per_serving = analysis.per_serving_analysis
    print(f"  Calories: {per_serving.calories_per_serving:.1f} kcal")
    
    for macro, percent in per_serving.macronutrient_distribution.items():
        print(f"  {macro.capitalize()}: {percent:.1f}%")
    
    # Print key nutrients
    for nutrient_id in ["protein", "fat", "carbohydrate", "fiber", "vitamin_c", "potassium"]:
        nutrient_value = per_serving.get_nutrient(nutrient_id)
        if nutrient_value:
            dri_percent = f"{nutrient_value.dri_percent:.1f}%" if nutrient_value.dri_percent is not None else "N/A"
            print(f"  {nutrient_value.nutrient.display_name}: {nutrient_value.amount:.1f} {nutrient_value.unit} ({dri_percent} of DRI)")


if __name__ == "__main__":
    main()