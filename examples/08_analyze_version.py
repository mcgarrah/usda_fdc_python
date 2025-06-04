#!/usr/bin/env python3
"""
Example of using the nutrient analysis command-line interface.

This script demonstrates how to use the fdc-nat command-line tool
by executing it as a subprocess. It's equivalent to running the commands
directly in the terminal.
"""

import os
import subprocess
import tempfile
from dotenv import load_dotenv

def run_command(command):
    """Run a command and print its output."""
    print(f"\n$ {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    return result

def main():
    # Load API key from environment variable
    load_dotenv()
    api_key = os.getenv("FDC_API_KEY")
    
    if not api_key:
        print("Error: FDC_API_KEY environment variable not set.")
        return
    
    # Set API key for commands
    os.environ["FDC_API_KEY"] = api_key
    
    print("=== USDA FDC Nutrient Analysis Tool Examples ===")
    
    # Example 1: Analyze a food
    print("\n=== Example 1: Analyze a food ===")
    run_command("fdc-nat analyze 1750340 --serving-size 100")
    
    # Example 2: Analyze a food with HTML output
    print("\n=== Example 2: Analyze a food with HTML output ===")
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp:
        html_file = temp.name
    
    run_command(f"fdc-nat analyze 1750340 --format html --output {html_file}")
    print(f"HTML report saved to {html_file}")
    
    # Example 3: Compare foods
    print("\n=== Example 3: Compare foods ===")
    run_command("fdc-nat compare 1750340 1750341 1750342 --nutrients vitamin_c,potassium,fiber")
    
    # Example 4: Analyze a recipe
    print("\n=== Example 4: Analyze a recipe ===")
    
    # Create a temporary file with ingredients
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
        temp.write("1 apple\n")
        temp.write("1 banana\n")
        temp.write("100g strawberries\n")
        ingredients_file = temp.name
    
    run_command(f"fdc-nat recipe --name 'Fruit Salad' --ingredients-file {ingredients_file} --servings 2")
    
    # Clean up temporary files
    os.unlink(html_file)
    os.unlink(ingredients_file)
    
    print("\nAll examples completed.")

if __name__ == "__main__":
    main()