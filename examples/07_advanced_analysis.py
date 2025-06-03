#!/usr/bin/env python3
"""
Advanced example of nutrient analysis using the USDA FDC API.

This example demonstrates:
- Creating a meal plan
- Analyzing nutrient content across multiple meals
- Generating visualizations
- Comparing to dietary reference intakes
"""

import os
import json
from dotenv import load_dotenv
from usda_fdc import FdcClient
from usda_fdc.analysis import analyze_food, analyze_foods, DriType, Gender
from usda_fdc.analysis.recipe import create_recipe, analyze_recipe
from usda_fdc.analysis.visualization import (
    generate_html_report,
    generate_macronutrient_chart_data,
    generate_dri_chart_data
)

class MealPlan:
    """Simple meal plan class for demonstration purposes."""
    
    def __init__(self, name, client):
        self.name = name
        self.client = client
        self.meals = []
    
    def add_meal(self, name, ingredients):
        """Add a meal to the plan."""
        recipe = create_recipe(
            name=name,
            ingredient_texts=ingredients,
            client=self.client,
            servings=1
        )
        self.meals.append(recipe)
        return recipe
    
    def analyze(self):
        """Analyze the entire meal plan."""
        meal_analyses = []
        for meal in self.meals:
            analysis = analyze_recipe(meal, dri_type=DriType.RDA, gender=Gender.MALE)
            meal_analyses.append(analysis.per_serving_analysis)
        
        return meal_analyses

def main():
    # Load API key from environment variable
    load_dotenv()
    api_key = os.getenv("FDC_API_KEY")
    
    if not api_key:
        print("Error: FDC_API_KEY environment variable not set.")
        return
    
    # Initialize the client
    client = FdcClient(api_key)
    
    # Create a meal plan for a day
    print("Creating a daily meal plan...")
    meal_plan = MealPlan("Daily Plan", client)
    
    # Add breakfast
    breakfast = meal_plan.add_meal(
        "Breakfast",
        [
            "1 cup oatmeal",
            "1 banana",
            "1 tbsp honey",
            "1/4 cup almonds"
        ]
    )
    
    # Add lunch
    lunch = meal_plan.add_meal(
        "Lunch",
        [
            "2 slices whole wheat bread",
            "3 oz chicken breast",
            "1 leaf lettuce",
            "1 slice tomato",
            "1 tbsp mayonnaise"
        ]
    )
    
    # Add dinner
    dinner = meal_plan.add_meal(
        "Dinner",
        [
            "6 oz salmon fillet",
            "1 cup brown rice",
            "1 cup broccoli",
            "1 tbsp olive oil"
        ]
    )
    
    # Add snack
    snack = meal_plan.add_meal(
        "Snack",
        [
            "1 apple",
            "2 tbsp peanut butter"
        ]
    )
    
    # Analyze the meal plan
    print("Analyzing meal plan...")
    meal_analyses = meal_plan.analyze()
    
    # Print summary of each meal
    print("\nMeal Plan Summary:")
    total_calories = 0
    
    for meal, analysis in zip(meal_plan.meals, meal_analyses):
        calories = analysis.calories_per_serving
        total_calories += calories
        print(f"\n{meal.name} ({meal.get_weight_per_serving():.0f}g):")
        print(f"- Calories: {calories:.0f} kcal")
        
        # Print macronutrient distribution
        for macro, percent in analysis.macronutrient_distribution.items():
            print(f"- {macro.capitalize()}: {percent:.1f}%")
    
    print(f"\nTotal daily calories: {total_calories:.0f} kcal")
    
    # Analyze key nutrients across the day
    print("\nKey Nutrient Summary (% of daily DRI):")
    key_nutrients = ["protein", "fiber", "vitamin_c", "calcium", "iron", "vitamin_a"]
    
    for nutrient_id in key_nutrients:
        total_amount = 0
        unit = ""
        dri_percent = 0
        
        for analysis in meal_analyses:
            nutrient_value = analysis.get_nutrient(nutrient_id)
            if nutrient_value:
                total_amount += nutrient_value.amount
                unit = nutrient_value.unit
                if nutrient_value.dri_percent:
                    dri_percent += nutrient_value.dri_percent
        
        if total_amount > 0:
            print(f"- {nutrient_id.capitalize()}: {total_amount:.1f} {unit} ({dri_percent:.1f}% of DRI)")
    
    # Generate visualization for breakfast
    print("\nGenerating visualization for breakfast...")
    breakfast_analysis = meal_analyses[0]
    
    # Generate chart data
    macro_chart = generate_macronutrient_chart_data(breakfast_analysis)
    dri_chart = generate_dri_chart_data(breakfast_analysis)
    
    # Save chart data to files
    with open("breakfast_macro_chart.json", "w") as f:
        json.dump(macro_chart, f, indent=2)
    
    with open("breakfast_dri_chart.json", "w") as f:
        json.dump(dri_chart, f, indent=2)
    
    print("Chart data saved to breakfast_macro_chart.json and breakfast_dri_chart.json")
    
    # Generate HTML report for breakfast
    html_report = generate_html_report(breakfast_analysis)
    with open("breakfast_report.html", "w") as f:
        f.write(html_report)
    
    print("HTML report saved to breakfast_report.html")
    
    # Advanced analysis: Find meals high in specific nutrients
    print("\nMeals high in specific nutrients:")
    
    # Find meal highest in protein
    protein_amounts = []
    for i, analysis in enumerate(meal_analyses):
        protein = analysis.get_nutrient("protein")
        if protein:
            protein_amounts.append((i, protein.amount))
    
    if protein_amounts:
        highest_protein = max(protein_amounts, key=lambda x: x[1])
        meal_index, amount = highest_protein
        meal_name = meal_plan.meals[meal_index].name
        print(f"- Highest protein: {meal_name} ({amount:.1f}g)")
    
    # Find meal highest in vitamin C
    vitc_amounts = []
    for i, analysis in enumerate(meal_analyses):
        vitc = analysis.get_nutrient("vitamin_c")
        if vitc:
            vitc_amounts.append((i, vitc.amount))
    
    if vitc_amounts:
        highest_vitc = max(vitc_amounts, key=lambda x: x[1])
        meal_index, amount = highest_vitc
        meal_name = meal_plan.meals[meal_index].name
        print(f"- Highest vitamin C: {meal_name} ({amount:.1f}mg)")

if __name__ == "__main__":
    main()