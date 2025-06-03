"""
Command-line interface for nutrient analysis.
"""

import argparse
import json
import os
import sys
from typing import List, Optional, Dict, Any

from ..client import FdcClient
from .analysis import analyze_food, analyze_foods, compare_foods
from .dri import DriType, Gender
from .visualization import generate_html_report
from .recipe import create_recipe, analyze_recipe


def analyze_command(args: argparse.Namespace) -> None:
    """Handle the analyze command."""
    client = FdcClient(args.api_key)
    
    try:
        # Get the food
        food = client.get_food(args.fdc_id)
        
        # Analyze the food
        dri_type = DriType.RDA if args.dri_type == "rda" else DriType.UL
        gender = Gender.MALE if args.gender == "male" else Gender.FEMALE
        analysis = analyze_food(
            food,
            dri_type=dri_type,
            gender=gender,
            serving_size=args.serving_size
        )
        
        # Output the analysis
        if args.format == "json":
            print(json.dumps(analysis.to_dict(), indent=2))
        elif args.format == "html":
            html = generate_html_report(analysis)
            if args.output:
                with open(args.output, "w") as f:
                    f.write(html)
                print(f"HTML report saved to {args.output}")
            else:
                print(html)
        else:  # text format
            print(f"Nutrient Analysis for {food.description}")
            print(f"FDC ID: {food.fdc_id}")
            print(f"Data Type: {food.data_type}")
            print(f"Serving Size: {args.serving_size}g")
            print(f"Calories: {analysis.calories_per_serving:.1f} kcal")
            print()
            
            print("Macronutrient Distribution:")
            for macro, percent in analysis.macronutrient_distribution.items():
                print(f"  {macro.capitalize()}: {percent:.1f}%")
            print()
            
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
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def compare_command(args: argparse.Namespace) -> None:
    """Handle the compare command."""
    client = FdcClient(args.api_key)
    
    try:
        # Get the foods
        foods = [client.get_food(fdc_id) for fdc_id in args.fdc_ids]
        
        # Compare the foods
        comparison = compare_foods(
            foods,
            nutrient_ids=args.nutrients.split(",") if args.nutrients else None,
            serving_sizes=[args.serving_size] * len(foods)
        )
        
        # Output the comparison
        if args.format == "json":
            # Convert to a more JSON-friendly format
            json_comparison = {}
            for nutrient_id, values in comparison.items():
                json_comparison[nutrient_id] = [
                    {"food": food, "amount": amount, "unit": unit}
                    for food, amount, unit in values
                ]
            print(json.dumps(json_comparison, indent=2))
        else:  # text format
            print(f"Nutrient Comparison (serving size: {args.serving_size}g)")
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
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def recipe_command(args: argparse.Namespace) -> None:
    """Handle the recipe command."""
    client = FdcClient(args.api_key)
    
    try:
        # Read ingredients from file if provided
        if args.ingredients_file:
            with open(args.ingredients_file, "r") as f:
                ingredient_texts = [line.strip() for line in f if line.strip()]
        else:
            # Read ingredients from command line
            ingredient_texts = args.ingredients
        
        # Create the recipe
        recipe = create_recipe(
            name=args.name,
            ingredient_texts=ingredient_texts,
            client=client,
            servings=args.servings
        )
        
        # Analyze the recipe
        dri_type = DriType.RDA if args.dri_type == "rda" else DriType.UL
        gender = Gender.MALE if args.gender == "male" else Gender.FEMALE
        analysis = analyze_recipe(
            recipe,
            dri_type=dri_type,
            gender=gender
        )
        
        # Output the analysis
        if args.format == "json":
            # Convert to a JSON-friendly format
            json_analysis = {
                "recipe": {
                    "name": recipe.name,
                    "servings": recipe.servings,
                    "total_weight_g": recipe.total_weight_g,
                    "weight_per_serving": recipe.get_weight_per_serving(),
                    "ingredients": [
                        {
                            "food": ingredient.food.description,
                            "amount": ingredient.amount,
                            "unit": ingredient.unit,
                            "weight_g": ingredient.weight_g
                        }
                        for ingredient in recipe.ingredients
                    ]
                },
                "per_serving": analysis.per_serving_analysis.to_dict(),
                "total": analysis.total_analysis.to_dict()
            }
            print(json.dumps(json_analysis, indent=2))
        else:  # text format
            print(f"Recipe Analysis for {recipe.name}")
            print(f"Servings: {recipe.servings}")
            print(f"Total Weight: {recipe.total_weight_g:.1f}g")
            print(f"Weight per Serving: {recipe.get_weight_per_serving():.1f}g")
            print()
            
            print("Ingredients:")
            for ingredient in recipe.ingredients:
                print(f"  {ingredient.amount} {ingredient.unit} {ingredient.food.description} ({ingredient.weight_g:.1f}g)")
            print()
            
            print("Nutrition per Serving:")
            per_serving = analysis.per_serving_analysis
            print(f"  Calories: {per_serving.calories_per_serving:.1f} kcal")
            
            for macro, percent in per_serving.macronutrient_distribution.items():
                print(f"  {macro.capitalize()}: {percent:.1f}%")
            
            for nutrient_id in ["protein", "fat", "carbohydrate", "fiber"]:
                nutrient_value = per_serving.get_nutrient(nutrient_id)
                if nutrient_value:
                    dri_percent = f"{nutrient_value.dri_percent:.1f}%" if nutrient_value.dri_percent is not None else "N/A"
                    print(f"  {nutrient_value.nutrient.display_name}: {nutrient_value.amount:.1f} {nutrient_value.unit} ({dri_percent} of DRI)")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="USDA FDC Nutrient Analysis CLI"
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("FDC_API_KEY"),
        help="FDC API key (can also be set via FDC_API_KEY environment variable)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a food")
    analyze_parser.add_argument("fdc_id", help="FDC ID of the food")
    analyze_parser.add_argument(
        "--serving-size",
        type=float,
        default=100.0,
        help="Serving size in grams (default: 100)"
    )
    analyze_parser.add_argument(
        "--dri-type",
        choices=["rda", "ul"],
        default="rda",
        help="DRI type to use (default: rda)"
    )
    analyze_parser.add_argument(
        "--gender",
        choices=["male", "female"],
        default="male",
        help="Gender to use for DRI comparison (default: male)"
    )
    analyze_parser.add_argument(
        "--format",
        choices=["text", "json", "html"],
        default="text",
        help="Output format (default: text)"
    )
    analyze_parser.add_argument(
        "--output",
        help="Output file for HTML format (default: stdout)"
    )
    analyze_parser.set_defaults(func=analyze_command)
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare foods")
    compare_parser.add_argument(
        "fdc_ids",
        nargs="+",
        help="FDC IDs of the foods to compare"
    )
    compare_parser.add_argument(
        "--nutrients",
        help="Comma-separated list of nutrient IDs to compare (default: all)"
    )
    compare_parser.add_argument(
        "--serving-size",
        type=float,
        default=100.0,
        help="Serving size in grams (default: 100)"
    )
    compare_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    compare_parser.set_defaults(func=compare_command)
    
    # Recipe command
    recipe_parser = subparsers.add_parser("recipe", help="Analyze a recipe")
    recipe_parser.add_argument(
        "--name",
        default="Recipe",
        help="Name of the recipe (default: Recipe)"
    )
    recipe_parser.add_argument(
        "--ingredients",
        nargs="+",
        default=[],
        help="Ingredients (e.g., '1 cup flour')"
    )
    recipe_parser.add_argument(
        "--ingredients-file",
        help="File containing ingredients (one per line)"
    )
    recipe_parser.add_argument(
        "--servings",
        type=int,
        default=1,
        help="Number of servings (default: 1)"
    )
    recipe_parser.add_argument(
        "--dri-type",
        choices=["rda", "ul"],
        default="rda",
        help="DRI type to use (default: rda)"
    )
    recipe_parser.add_argument(
        "--gender",
        choices=["male", "female"],
        default="male",
        help="Gender to use for DRI comparison (default: male)"
    )
    recipe_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    recipe_parser.set_defaults(func=recipe_command)
    
    args = parser.parse_args()
    
    # Check if API key is provided
    if not args.api_key:
        print("Error: No API key provided. Use --api-key or set FDC_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)
    
    # Execute command if provided
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()