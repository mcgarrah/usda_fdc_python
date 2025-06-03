"""
Command-line interface for the USDA FDC client.
"""

import argparse
import json
import os
import sys
from typing import List, Optional, Dict, Any

from dotenv import load_dotenv

from . import __version__
from .client import FdcClient
from .exceptions import FdcApiError

def format_output(data: Any, output_format: str) -> str:
    """Format output data based on specified format."""
    if output_format == "json":
        return json.dumps(data, indent=2, default=lambda o: o.__dict__)
    elif output_format == "pretty":
        if hasattr(data, "__dict__"):
            return pretty_print_object(data)
        elif isinstance(data, list):
            return "\n\n".join(pretty_print_object(item) for item in data)
        else:
            return str(data)
    return str(data)

def pretty_print_object(obj: Any) -> str:
    """Pretty print an object."""
    if hasattr(obj, "description") and hasattr(obj, "fdc_id"):
        result = [f"{obj.description} (FDC ID: {obj.fdc_id})"]
        
        # Add basic food info
        if hasattr(obj, "data_type") and obj.data_type:
            result.append(f"Type: {obj.data_type}")
        if hasattr(obj, "brand_owner") and obj.brand_owner:
            result.append(f"Brand: {obj.brand_owner}")
        if hasattr(obj, "ingredients") and obj.ingredients:
            result.append(f"Ingredients: {obj.ingredients}")
        
        # Add nutrients if available
        if hasattr(obj, "nutrients") and obj.nutrients:
            result.append("\nNutrients (per 100g):")
            for nutrient in sorted(obj.nutrients, key=lambda n: n.name):
                result.append(f"  {nutrient.name}: {nutrient.amount} {nutrient.unit_name}")
        
        # Add portions if available
        if hasattr(obj, "food_portions") and obj.food_portions:
            result.append("\nPortions:")
            for portion in obj.food_portions:
                desc = portion.portion_description or portion.measure_unit or "serving"
                result.append(f"  {portion.amount} {desc} = {portion.gram_weight}g")
        
        return "\n".join(result)
    
    return str(obj.__dict__)

def search_command(args: argparse.Namespace) -> None:
    """Handle search command."""
    client = FdcClient(args.api_key)
    try:
        results = client.search(
            query=args.query,
            data_type=args.data_type,
            page_size=args.page_size,
            page_number=args.page_number
        )
        
        print(f"Found {results.total_hits} results (page {results.current_page} of {results.total_pages})")
        for food in results.foods:
            print(format_output(food, args.format))
            if args.format != "json":
                print("-" * 40)
    except FdcApiError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def food_command(args: argparse.Namespace) -> None:
    """Handle food command."""
    client = FdcClient(args.api_key)
    try:
        food = client.get_food(args.fdc_id)
        print(format_output(food, args.format))
    except FdcApiError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def nutrients_command(args: argparse.Namespace) -> None:
    """Handle nutrients command."""
    client = FdcClient(args.api_key)
    try:
        food = client.get_food(args.fdc_id)
        if args.format == "json":
            print(format_output(food.nutrients, args.format))
        else:
            print(f"Nutrients for {food.description} (FDC ID: {food.fdc_id}):")
            for nutrient in sorted(food.nutrients, key=lambda n: n.name):
                print(f"  {nutrient.name}: {nutrient.amount} {nutrient.unit_name}")
    except FdcApiError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def list_command(args: argparse.Namespace) -> None:
    """Handle list command."""
    client = FdcClient(args.api_key)
    try:
        foods = client.list_foods(
            data_type=args.data_type,
            page_size=args.page_size,
            page_number=args.page_number
        )
        
        print(f"Listing {len(foods)} foods (page {args.page_number}):")
        for food in foods:
            print(format_output(food, args.format))
            if args.format != "json":
                print("-" * 40)
    except FdcApiError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main() -> None:
    """Main entry point for the CLI."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        prog="fdc",
        description="USDA Food Data Central (FDC) command-line interface"
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
    parser.add_argument(
        "--format", 
        choices=["json", "pretty", "text"], 
        default="pretty",
        help="Output format (default: pretty)"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for foods")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--data-type", nargs="+", help="Filter by data type")
    search_parser.add_argument("--page-size", type=int, default=10, help="Results per page")
    search_parser.add_argument("--page-number", type=int, default=1, help="Page number")
    search_parser.set_defaults(func=search_command)
    
    # Food command
    food_parser = subparsers.add_parser("food", help="Get food details")
    food_parser.add_argument("fdc_id", help="FDC ID of the food")
    food_parser.set_defaults(func=food_command)
    
    # Nutrients command
    nutrients_parser = subparsers.add_parser("nutrients", help="Get food nutrients")
    nutrients_parser.add_argument("fdc_id", help="FDC ID of the food")
    nutrients_parser.set_defaults(func=nutrients_command)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List foods")
    list_parser.add_argument("--data-type", nargs="+", help="Filter by data type")
    list_parser.add_argument("--page-size", type=int, default=10, help="Results per page")
    list_parser.add_argument("--page-number", type=int, default=1, help="Page number")
    list_parser.set_defaults(func=list_command)
    
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