Examples
========

This section provides detailed examples of how to use the USDA FDC Python Client library. All example scripts can be found in the ``examples`` directory of the repository.

Basic Examples
------------

Basic Search
^^^^^^^^^^^

The ``01_basic_search.py`` example demonstrates how to search for foods using the USDA FDC API:

.. code-block:: python

   from usda_fdc import FdcClient
   
   # Initialize the client
   client = FdcClient("YOUR_API_KEY")
   
   # Search for foods containing "apple"
   results = client.search("apple", page_size=5)
   
   # Print search results
   print(f"Found {results.total_hits} results (showing first 5)")
   for food in results.foods:
       print(f"- {food.description} (FDC ID: {food.fdc_id}, Type: {food.data_type})")
   
   # Search with data type filter
   branded_results = client.search("apple", data_type=["Branded"], page_size=5)

This example shows:

- How to initialize the client with your API key
- How to search for foods with keywords
- How to access search results
- How to filter search results by data type

Food Details
^^^^^^^^^^

The ``02_food_details.py`` example shows how to retrieve detailed information about specific foods:

.. code-block:: python

   from usda_fdc import FdcClient
   
   # Initialize the client
   client = FdcClient("YOUR_API_KEY")
   
   # Get food by FDC ID (Apple, raw, with skin)
   food = client.get_food(1750340)
   
   # Print basic food information
   print(f"Food: {food.description}")
   print(f"FDC ID: {food.fdc_id}")
   print(f"Data Type: {food.data_type}")
   
   # Print nutrient information
   for nutrient in food.nutrients[:10]:
       print(f"- {nutrient.name}: {nutrient.amount} {nutrient.unit_name}")
   
   # Get multiple foods at once
   foods = client.get_foods([1750340, 1750341, 1750342])  # Apple, Banana, Orange

This example demonstrates:

- How to retrieve a specific food by its FDC ID
- How to access food properties like description, data type, etc.
- How to access nutrient information
- How to retrieve multiple foods at once

Nutrient Analysis Examples
-----------------------

Nutrient Analysis
^^^^^^^^^^^^^^^

The ``03_nutrient_analysis.py`` example demonstrates how to analyze the nutrient content of a food:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.analysis import analyze_food, DriType, Gender
   
   # Initialize the client
   client = FdcClient("YOUR_API_KEY")
   
   # Get food by FDC ID
   food = client.get_food(1750340)
   
   # Analyze the food
   analysis = analyze_food(
       food,
       dri_type=DriType.RDA,
       gender=Gender.MALE,
       serving_size=100.0
   )
   
   # Print basic analysis information
   print(f"Calories: {analysis.calories_per_serving:.1f} kcal")
   
   # Print macronutrient distribution
   for macro, percent in analysis.macronutrient_distribution.items():
       print(f"- {macro.capitalize()}: {percent:.1f}%")
   
   # Print key nutrients with DRI percentages
   for nutrient_id in ["protein", "fiber", "vitamin_c"]:
       nutrient_value = analysis.get_nutrient(nutrient_id)
       if nutrient_value:
           dri_percent = f"{nutrient_value.dri_percent:.1f}%" if nutrient_value.dri_percent is not None else "N/A"
           print(f"- {nutrient_value.nutrient.display_name}: {nutrient_value.amount:.1f} {nutrient_value.unit} ({dri_percent} of DRI)")

This example shows:

- How to analyze the nutrient content of a food
- How to specify serving size and DRI type
- How to access macronutrient distribution
- How to compare nutrient content to dietary reference intakes

Compare Foods
^^^^^^^^^^^

The ``04_compare_foods.py`` example demonstrates how to compare the nutrient content of multiple foods:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.analysis import compare_foods
   
   # Initialize the client
   client = FdcClient("YOUR_API_KEY")
   
   # Get foods to compare
   foods = [
       client.get_food(1750340),  # Apple, raw, with skin
       client.get_food(1750341),  # Banana, raw
       client.get_food(1750342)   # Orange, raw, all commercial varieties
   ]
   
   # Compare the foods
   comparison = compare_foods(
       foods,
       nutrient_ids=["vitamin_c", "potassium", "fiber", "sugar"],
       serving_sizes=[100.0, 100.0, 100.0]
   )
   
   # Print the comparison
   for nutrient_id, values in comparison.items():
       print(f"\n{nutrient_id.capitalize()}:")
       for food, amount, unit in values:
           print(f"- {food}: {amount:.1f} {unit}")

This example demonstrates:

- How to compare multiple foods
- How to specify which nutrients to compare
- How to use different serving sizes for comparison
- How to access and display comparison results

Recipe Analysis
^^^^^^^^^^^^

The ``05_recipe_analysis.py`` example shows how to create and analyze recipes:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.analysis import DriType, Gender
   from usda_fdc.analysis.recipe import create_recipe, analyze_recipe
   
   # Initialize the client
   client = FdcClient("YOUR_API_KEY")
   
   # Define a recipe
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

This example demonstrates:

- How to create a recipe from ingredient descriptions
- How to specify the number of servings
- How to analyze the nutrient content of a recipe
- How to access per-serving nutrient information

Advanced Examples
--------------

Django Integration
^^^^^^^^^^^^^^^

The ``06_django_integration.py`` example demonstrates how to use the library with Django:

.. code-block:: python

   from usda_fdc.django import FdcCache
   
   # Initialize the cache
   cache = FdcCache(api_key="YOUR_API_KEY")
   
   # Search for foods (results will be cached in Django models)
   results = cache.search("apple", page_size=5)
   
   # Get a food by FDC ID (will be cached in Django models)
   food = cache.get_food(1750340)
   
   # Force refresh from API
   refreshed_food = cache.get_food(1750340, force_refresh=True)
   
   # Batch operations
   cache.refresh([1750340, 1750341, 1750342])

This example shows:

- How to initialize the Django cache
- How to search for foods and cache the results
- How to retrieve foods from the cache or API
- How to force refresh cached data
- How to perform batch operations

Advanced Analysis
^^^^^^^^^^^^^^^

The ``07_advanced_analysis.py`` example demonstrates advanced nutrient analysis features:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.analysis import analyze_food, DriType, Gender
   from usda_fdc.analysis.recipe import create_recipe, analyze_recipe
   from usda_fdc.analysis.visualization import generate_html_report
   
   # Create a meal plan
   class MealPlan:
       def __init__(self, name, client):
           self.name = name
           self.client = client
           self.meals = []
       
       def add_meal(self, name, ingredients):
           recipe = create_recipe(name=name, ingredient_texts=ingredients, client=self.client, servings=1)
           self.meals.append(recipe)
           return recipe
       
       def analyze(self):
           meal_analyses = []
           for meal in self.meals:
               analysis = analyze_recipe(meal)
               meal_analyses.append(analysis.per_serving_analysis)
           return meal_analyses
   
   # Create and analyze a meal plan
   meal_plan = MealPlan("Daily Plan", client)
   meal_plan.add_meal("Breakfast", ["1 cup oatmeal", "1 banana", "1 tbsp honey"])
   meal_plan.add_meal("Lunch", ["2 slices bread", "3 oz chicken", "1 leaf lettuce"])
   meal_analyses = meal_plan.analyze()
   
   # Generate visualization
   html_report = generate_html_report(meal_analyses[0])
   with open("breakfast_report.html", "w") as f:
       f.write(html_report)

This example demonstrates:

- How to create a meal plan with multiple meals
- How to analyze nutrient content across multiple meals
- How to generate visualizations and HTML reports
- How to perform advanced analysis on meal data

Command-Line Interface
^^^^^^^^^^^^^^^^^^^

The ``08_analyze_version.py`` example demonstrates the nutrient analysis command-line interface:

.. code-block:: python

   import subprocess
   
   # Analyze a food
   subprocess.run("fdc-nat analyze 1750340 --serving-size 100", shell=True)
   
   # Compare foods
   subprocess.run("fdc-nat compare 1750340 1750341 1750342 --nutrients vitamin_c,potassium,fiber", shell=True)
   
   # Analyze a recipe
   subprocess.run("fdc-nat recipe --name 'Fruit Salad' --ingredients '1 apple' '1 banana' '100g strawberries'", shell=True)

This example shows:

- How to use the nutrient analysis CLI
- How to analyze a food from the command line
- How to compare foods from the command line
- How to analyze a recipe from the command line

Running the Examples
-----------------

To run these examples, you'll need:

1. An API key from the USDA Food Data Central API
2. The USDA FDC Python Client library installed

You can set your API key as an environment variable:

.. code-block:: bash

   export FDC_API_KEY=your_api_key_here

Or create a ``.env`` file in the same directory as the examples:

.. code-block:: bash

   FDC_API_KEY=your_api_key_here

Then run the examples:

.. code-block:: bash

   python examples/01_basic_search.py