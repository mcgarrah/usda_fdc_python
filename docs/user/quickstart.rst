Quickstart
==========

This guide will help you get started with the USDA Food Data Central (FDC) Python Client.

Basic Setup
----------

First, import the client and initialize it with your API key:

.. code-block:: python

   from usda_fdc import FdcClient
   import os
   from dotenv import load_dotenv
   
   # Load API key from .env file
   load_dotenv()
   api_key = os.getenv("FDC_API_KEY")
   
   # Initialize client
   client = FdcClient(api_key)

Searching for Foods
-----------------

Search for foods using keywords:

.. code-block:: python

   # Search for foods containing "apple"
   results = client.search("apple")
   
   # Print search results
   print(f"Found {results.total_hits} results")
   for food in results.foods:
       print(f"{food.description} (FDC ID: {food.fdc_id})")

Getting Food Details
-----------------

Retrieve detailed information about a specific food:

.. code-block:: python

   # Get food by FDC ID
   food = client.get_food(1750340)
   
   # Print food details
   print(f"Food: {food.description}")
   print(f"Data Type: {food.data_type}")
   print(f"Brand: {food.brand_name}")
   
   # Print nutrients
   print("\\nNutrients:")
   for nutrient in food.nutrients:
       print(f"{nutrient.name}: {nutrient.amount} {nutrient.unit_name}")

Getting Multiple Foods
-------------------

Retrieve information about multiple foods at once:

.. code-block:: python

   # Get multiple foods by FDC ID
   foods = client.get_foods([1750340, 1750341, 1750342])
   
   # Process foods
   for food in foods:
       print(f"{food.description} ({food.data_type})")

Listing Foods
-----------

Get a paged list of foods:

.. code-block:: python

   # List foods with pagination
   foods = client.list_foods(page_size=10, page_number=1)
   
   # Process foods
   for food in foods:
       print(f"{food.description} (FDC ID: {food.fdc_id})")

   # Get next page
   next_page = client.list_foods(page_size=10, page_number=2)

Filtering by Data Type
-------------------

Filter foods by data type:

.. code-block:: python

   # Get only branded foods
   branded_foods = client.list_foods(data_type=["Branded"])
   
   # Get foundation and SR Legacy foods
   foundation_foods = client.list_foods(data_type=["Foundation", "SR Legacy"])

Analyzing Nutrient Content
-----------------------

Analyze the nutrient content of a food:

.. code-block:: python

   from usda_fdc.analysis import analyze_food, DriType, Gender
   
   # Get a food
   food = client.get_food(1750340)  # Apple, raw, with skin
   
   # Analyze the food
   analysis = analyze_food(
       food,
       dri_type=DriType.RDA,
       gender=Gender.MALE,
       serving_size=100.0
   )
   
   # Access the analysis results
   print(f"Calories: {analysis.calories_per_serving} kcal")
   print(f"Protein: {analysis.get_nutrient('protein').amount} g")
   
   # Check DRI percentages
   vitamin_c = analysis.get_nutrient('vitamin_c')
   if vitamin_c and vitamin_c.dri_percent:
       print(f"Vitamin C: {vitamin_c.amount} mg ({vitamin_c.dri_percent:.1f}% of DRI)")

Comparing Foods
------------

Compare the nutrient content of multiple foods:

.. code-block:: python

   from usda_fdc.analysis import compare_foods
   
   # Get foods to compare
   foods = [
       client.get_food(1750340),  # Apple
       client.get_food(1750341),  # Banana
       client.get_food(1750342)   # Orange
   ]
   
   # Compare the foods
   comparison = compare_foods(
       foods,
       nutrient_ids=["vitamin_c", "potassium", "fiber"],
       serving_sizes=[100.0, 100.0, 100.0]
   )
   
   # Print the comparison
   for nutrient_id, values in comparison.items():
       print(f"{nutrient_id}:")
       for food, amount, unit in values:
           print(f"  {food}: {amount:.1f} {unit}")

Analyzing Recipes
--------------

Create and analyze a recipe:

.. code-block:: python

   from usda_fdc.analysis.recipe import create_recipe, analyze_recipe
   
   # Create a recipe
   recipe = create_recipe(
       name="Fruit Salad",
       ingredient_texts=[
           "1 apple",
           "1 banana",
           "100g strawberries"
       ],
       client=client,
       servings=2
   )
   
   # Analyze the recipe
   analysis = analyze_recipe(recipe)
   
   # Access the analysis results
   per_serving = analysis.per_serving_analysis
   print(f"Calories per serving: {per_serving.calories_per_serving:.1f} kcal")
   print(f"Protein per serving: {per_serving.get_nutrient('protein').amount:.1f} g")

Command Line Interface
--------------------

The library includes a command-line tool called ``fdc`` that provides quick access to common operations:

.. code-block:: bash

   # Search for foods
   fdc search "apple"
   
   # Get food details
   fdc food 1750340
   
   # Get nutrients for a food
   fdc nutrients 1750340
   
   # List foods with pagination
   fdc list --page-size 5 --page-number 1

For nutrient analysis, use the ``fdc-nat`` command:

.. code-block:: bash

   # Analyze a food
   fdc-nat analyze 1750340 --serving-size 100
   
   # Compare foods
   fdc-nat compare 1750340 1750341 1750342 --nutrients vitamin_c,potassium,fiber
   
   # Analyze a recipe
   fdc-nat recipe --name "Fruit Salad" --ingredients "1 apple" "1 banana" "100g strawberries"

Error Handling
------------

Handle errors properly:

.. code-block:: python

   from usda_fdc import FdcClient, FdcApiError, FdcAuthError
   
   try:
       food = client.get_food(1750340)
   except FdcAuthError as e:
       print(f"Authentication failed: {e}")
   except FdcApiError as e:
       print(f"API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")