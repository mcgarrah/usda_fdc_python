"""
Command-line interface for nutrient analysis.
"""

import os
import sys
import json
import argparse
from typing import List, Optional, Dict, Any

from dotenv import load_dotenv

from .. import __version__
from ..client import FdcClient
from .analysis import analyze_food, compare_foods
from .dri import DriType, Gender
from .recipe import create_recipe, analyze_recipe
from .visualization import generate_html_report

def analyze_command(args: argparse.Namespace) -> None:
    """Handle analyze command."""
    client = FdcClient(args.api_key)
    
    try:
        # Get the food
        food = client.get_food(args.fdc_id)
        
        # Analyze the food
        analysis = analyze_food(
            food,
            serving_size=args.serving_size,
            dri_type=DriType(args.dri_type),
            gender=Gender(args.gender),
            age=args.age
        )
        
        # Output the analysis
        if args.format == "json":
            # Convert to JSON-serializable dict
            result = {
                "food": {
                    "fdc_id": food.fdc_id,
                    "description": food.description,
                    "data_type": food.data_type
                },
                "serving_size": analysis.serving_size,
                "calories": analysis.calories_per_serving,
                "macronutrients": {
                    "protein": analysis.protein_per_serving,
                    "carbs": analysis.carbs_per_serving,
                    "fat": analysis.fat_per_serving
                },
                "macronutrient_distribution": analysis.macronutrient_distribution,
                "nutrients": {
                    nutrient_id: {
                        "name": value.nutrient.name,
                        "amount": value.amount,
                        "unit": value.unit,
                        "dri": value.dri,
                        "dri_percent": value.dri_percent
                    }
                    for nutrient_id, value in analysis.nutrients.items()
                }
            }
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
            else:
                print(json.dumps(result, indent=2))
        
        elif args.format == "html":
            # Generate HTML report
            html = generate_html_report(analysis)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(html)
            else:
                print(html)
        
        else:  # text format
            print(f"Nutrient Analysis: {food.description}")
            print(f"Serving Size: {analysis.serving_size}g")
            print(f"Calories: {analysis.calories_per_serving:.1f} kcal")
            
            print("\nMacronutrient Distribution:")
            for macro, percent in analysis.macronutrient_distribution.items():
                print(f"- {macro.capitalize()}: {percent:.1f}%")
            
            print("\nKey Nutrients:")
            for nutrient_id in ["protein", "fiber", "vitamin_c", "calcium", "iron"]:
                nutrient_value = analysis.get_nutrient(nutrient_id)
                if nutrient_value:
                    dri_percent = f"{nutrient_value.dri_percent:.1f}%" if nutrient_value.dri_percent is not None else "N/A"
                    print(f"- {nutrient_value.nutrient.name}: {nutrient_value.amount:.1f} {nutrient_value.unit} ({dri_percent} of DRI)")
            
            if args.detailed:
                print("\nDetailed Nutrients:")
                for nutrient_id, value in sorted(
                    analysis.nutrients.items(),
                    key=lambda x: x[1].dri_percent or 0,
                    reverse=True
                ):
                    dri_percent = f"{value.dri_percent:.1f}%" if value.dri_percent is not None else "N/A"
                    print(f"- {value.nutrient.name}: {value.amount:.1f} {value.unit} ({dri_percent} of DRI)")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def compare_command(args: argparse.Namespace) -> None:
    """Handle compare command."""
    client = FdcClient(args.api_key)
    
    try:
        # Get the foods
        foods = [client.get_food(fdc_id) for fdc_id in args.fdc_ids]
        
        # Parse nutrient IDs
        nutrient_ids = args.nutrients.split(",") if args.nutrients else None
        
        # Compare the foods
        comparison = compare_foods(
            foods,
            nutrient_ids=nutrient_ids,
            serving_sizes=[args.serving_size] * len(foods),
            dri_type=DriType(args.dri_type),
            gender=Gender(args.gender),
            age=args.age
        )
        
        # Output the comparison
        if args.format == "json":
            # Convert to JSON-serializable dict
            result = {
                "foods": [
                    {
                        "fdc_id": food.fdc_id,
                        "description": food.description,
                        "data_type": food.data_type
                    }
                    for food in foods
                ],
                "serving_size": args.serving_size,
                "comparison": {
                    nutrient_id: [
                        {
                            "food": food_name,
                            "amount": amount,
                            "unit": unit
                        }
                        for food_name, amount, unit in values
                    ]
                    for nutrient_id, values in comparison.items()
                }
            }
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
            else:
                print(json.dumps(result, indent=2))
        
        else:  # text format
            print(f"Food Comparison (per {args.serving_size}g):")
            print(f"Foods: {', '.join(food.description for food in foods)}")
            
            print("\nNutrient Comparison:")
            for nutrient_id, values in comparison.items():
                if not values:
                    continue
                
                print(f"\n{nutrient_id.capitalize()}:")
                for food_name, amount, unit in values:
                    print(f"- {food_name}: {amount:.1f} {unit}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def recipe_command(args: argparse.Namespace) -> None:
    """Handle recipe command."""
    client = FdcClient(args.api_key)
    
    try:
        # Get ingredients
        ingredients = []
        if args.ingredients:
            ingredients = args.ingredients
        elif args.ingredients_file:
            with open(args.ingredients_file, 'r') as f:
                ingredients = [line.strip() for line in f if line.strip()]
        
        if not ingredients:
            print("Error: No ingredients provided.", file=sys.stderr)
            sys.exit(1)
        
        # Create the recipe
        recipe = create_recipe(
            name=args.name,
            ingredient_texts=ingredients,
            client=client,
            servings=args.servings
        )
        
        # Analyze the recipe
        analysis = analyze_recipe(
            recipe,
            dri_type=DriType(args.dri_type),
            gender=Gender(args.gender),
            age=args.age
        )
        
        # Output the analysis
        if args.format == "json":
            # Convert to JSON-serializable dict
            result = {
                "recipe": {
                    "name": recipe.name,
                    "servings": recipe.servings,
                    "total_weight_g": recipe.total_weight_g,
                    "weight_per_serving": recipe.get_weight_per_serving(),
                    "ingredients": [
                        {
                            "description": ingredient.description,
                            "food": {
                                "fdc_id": ingredient.food.fdc_id,
                                "description": ingredient.food.description
                            },
                            "weight_g": ingredient.weight_g
                        }
                        for ingredient in recipe.ingredients
                    ]
                },
                "per_serving": {
                    "calories": analysis.per_serving_analysis.calories_per_serving,
                    "macronutrients": {
                        "protein": analysis.per_serving_analysis.protein_per_serving,
                        "carbs": analysis.per_serving_analysis.carbs_per_serving,
                        "fat": analysis.per_serving_analysis.fat_per_serving
                    },
                    "macronutrient_distribution": analysis.per_serving_analysis.macronutrient_distribution,
                    "nutrients": {
                        nutrient_id: {
                            "name": value.nutrient.name,
                            "amount": value.amount,
                            "unit": value.unit,
                            "dri": value.dri,
                            "dri_percent": value.dri_percent
                        }
                        for nutrient_id, value in analysis.per_serving_analysis.nutrients.items()
                    }
                }
            }
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
            else:
                print(json.dumps(result, indent=2))
        
        elif args.format == "html":
            # Generate HTML report
            html = generate_html_report(analysis.per_serving_analysis)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(html)
            else:
                print(html)
        
        else:  # text format
            print(f"Recipe Analysis: {recipe.name}")
            print(f"Servings: {recipe.servings}")
            print(f"Total Weight: {recipe.total_weight_g:.1f}g")
            print(f"Weight per Serving: {recipe.get_weight_per_serving():.1f}g")
            
            print("\nIngredients:")
            for ingredient in recipe.ingredients:
                print(f"- {ingredient}")
            
            print("\nNutrition per Serving:")
            print(f"Calories: {analysis.per_serving_analysis.calories_per_serving:.1f} kcal")
            
            print("\nMacronutrient Distribution:")
            for macro, percent in analysis.per_serving_analysis.macronutrient_distribution.items():
                print(f"- {macro.capitalize()}: {percent:.1f}%")
            
            print("\nKey Nutrients per Serving:")
            for nutrient_id in ["protein", "fiber", "vitamin_c", "calcium", "iron"]:
                nutrient_value = analysis.per_serving_analysis.get_nutrient(nutrient_id)
                if nutrient_value:
                    dri_percent = f"{nutrient_value.dri_percent:.1f}%" if nutrient_value.dri_percent is not None else "N/A"
                    print(f"- {nutrient_value.nutrient.name}: {nutrient_value.amount:.1f} {nutrient_value.unit} ({dri_percent} of DRI)")
            
            if args.detailed:
                print("\nDetailed Nutrients per Serving:")
                for nutrient_id, value in sorted(
                    analysis.per_serving_analysis.nutrients.items(),
                    key=lambda x: x[1].dri_percent or 0,
                    reverse=True
                ):
                    dri_percent = f"{value.dri_percent:.1f}%" if value.dri_percent is not None else "N/A"
                    print(f"- {value.nutrient.name}: {value.amount:.1f} {value.unit} ({dri_percent} of DRI)")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main() -> None:
    """Main entry point for the CLI."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        prog="fdc-nat",
        description="USDA Food Data Central (FDC) Nutrient Analysis Tool"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--api-key", 
        default=os.environ.get("FDC_API_KEY"),
        help="FDC API key (can also be set via FDC_API_KEY environment variable)"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a food")
    analyze_parser.add_argument("fdc_id", help="FDC ID of the food")
    analyze_parser.add_argument("--serving-size", type=float, default=100.0, help="Serving size in grams")
    analyze_parser.add_argument("--dri-type", choices=[t.value for t in DriType], default=DriType.RDA.value, help="DRI type")
    analyze_parser.add_argument("--gender", choices=[g.value for g in Gender], default=Gender.MALE.value, help="Gender for DRI")
    analyze_parser.add_argument("--age", type=int, default=30, help="Age for DRI")
    analyze_parser.add_argument("--detailed", action="store_true", help="Show detailed nutrient information")
    analyze_parser.add_argument("--format", choices=["text", "json", "html"], default="text", help="Output format")
    analyze_parser.add_argument("--output", help="Output file (default: stdout)")
    analyze_parser.set_defaults(func=analyze_command)
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare foods")
    compare_parser.add_argument("fdc_ids", nargs="+", help="FDC IDs of the foods to compare")
    compare_parser.add_argument("--serving-size", type=float, default=100.0, help="Serving size in grams")
    compare_parser.add_argument("--nutrients", help="Comma-separated list of nutrient IDs to compare")
    compare_parser.add_argument("--dri-type", choices=[t.value for t in DriType], default=DriType.RDA.value, help="DRI type")
    compare_parser.add_argument("--gender", choices=[g.value for g in Gender], default=Gender.MALE.value, help="Gender for DRI")
    compare_parser.add_argument("--age", type=int, default=30, help="Age for DRI")
    compare_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    compare_parser.add_argument("--output", help="Output file (default: stdout)")
    compare_parser.set_defaults(func=compare_command)
    
    # Recipe command
    recipe_parser = subparsers.add_parser("recipe", help="Analyze a recipe")
    recipe_parser.add_argument("--name", default="Recipe", help="Recipe name")
    recipe_parser.add_argument("--ingredients", nargs="*", help="List of ingredients")
    recipe_parser.add_argument("--ingredients-file", help="File with ingredients (one per line)")
    recipe_parser.add_argument("--servings", type=int, default=1, help="Number of servings")
    recipe_parser.add_argument("--dri-type", choices=[t.value for t in DriType], default=DriType.RDA.value, help="DRI type")
    recipe_parser.add_argument("--gender", choices=[g.value for g in Gender], default=Gender.MALE.value, help="Gender for DRI")
    recipe_parser.add_argument("--age", type=int, default=30, help="Age for DRI")
    recipe_parser.add_argument("--detailed", action="store_true", help="Show detailed nutrient information")
    recipe_parser.add_argument("--format", choices=["text", "json", "html"], default="text", help="Output format")
    recipe_parser.add_argument("--output", help="Output file (default: stdout)")
    recipe_parser.set_defaults(func=recipe_command)
    
    # Parse arguments
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