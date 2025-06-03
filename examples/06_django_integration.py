#!/usr/bin/env python3
"""
Example of Django integration with the USDA FDC API.

Note: This example is for illustration purposes and requires Django to be installed
and properly configured. It's meant to be used within a Django project.
"""

import os
from dotenv import load_dotenv

# This would be in a Django view or management command
def django_example():
    """Example of using the USDA FDC API with Django integration."""
    # Load API key from environment variable
    load_dotenv()
    api_key = os.getenv("FDC_API_KEY")
    
    if not api_key:
        print("Error: FDC_API_KEY environment variable not set.")
        return
    
    # In a real Django project, you would import these
    try:
        from usda_fdc.django import FdcCache
    except ImportError:
        print("Django is not installed or not configured properly.")
        print("This example requires Django to be installed.")
        return
    
    # Initialize the cache
    cache = FdcCache(api_key=api_key)
    
    # Search for foods (results will be cached in Django models)
    print("Searching for 'apple' (results will be cached)...")
    results = cache.search("apple", page_size=5)
    
    print(f"Found {results.total_hits} results (showing first 5)")
    for food in results.foods:
        print(f"- {food.description} (FDC ID: {food.fdc_id})")
    
    # Get a food by FDC ID (will be cached in Django models)
    print("\nGetting food details (will be cached)...")
    food = cache.get_food(1750340)  # Apple, raw, with skin
    
    print(f"Retrieved: {food.description}")
    print(f"This food has {len(food.nutrients)} nutrients")
    
    # Check if the food is in the cache
    from usda_fdc.django.models import FoodModel
    
    try:
        cached_food = FoodModel.objects.get(fdc_id=1750340)
        print(f"\nFood found in cache: {cached_food.description}")
        print(f"Last updated: {cached_food.updated_at}")
        
        # Count nutrients in the database
        nutrient_count = cached_food.nutrients.count()
        print(f"Nutrients in database: {nutrient_count}")
    except FoodModel.DoesNotExist:
        print("\nFood not found in cache.")
    
    # Force refresh from API
    print("\nForcing refresh from API...")
    refreshed_food = cache.get_food(1750340, force_refresh=True)
    print(f"Refreshed: {refreshed_food.description}")
    
    # Batch operations
    print("\nRefreshing multiple foods at once...")
    cache.refresh([1750340, 1750341, 1750342])
    print("Multiple foods refreshed.")

if __name__ == "__main__":
    print("Note: This example requires Django to be installed and configured.")
    print("It's meant to be used within a Django project.")
    print("Running for illustration purposes only...\n")
    django_example()