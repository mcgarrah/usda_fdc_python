Examples
========

The USDA FDC Python Client includes several example scripts demonstrating how to use the library.

Basic Examples
------------

Basic Search
^^^^^^^^^^^

The ``01_basic_search.py`` example demonstrates how to search for foods using the USDA FDC API:

.. code-block:: python

   from usda_fdc import FdcClient

   # Initialize the client
   client = FdcClient("YOUR_API_KEY")

   # Search for foods
   results = client.search("apple")
   for food in results.foods:
       print(f"{food.description} (FDC ID: {food.fdc_id})")

Food Details
^^^^^^^^^^

The ``02_food_details.py`` example shows how to retrieve detailed information about specific foods:

.. code-block:: python

   from usda_fdc import FdcClient

   # Initialize the client
   client = FdcClient("YOUR_API_KEY")

   # Get food by FDC ID
   food = client.get_food(1750340)  # Apple, raw, with skin
   
   # Print food details
   print(f"Food: {food.description}")
   print(f"Data Type: {food.data_type}")
   
   # Print nutrients
   for nutrient in food.nutrients:
       print(f"{nutrient.name}: {nutrient.amount} {nutrient.unit_name}")

Nutrient Analysis Examples
-----------------------

Nutrient Analysis
^^^^^^^^^^^^^

The ``03_nutrient_analysis.py`` example demonstrates how to analyze the nutrient content of a food:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.analysis import analyze_food, DriType, Gender

   # Initialize the client
   client = FdcClient("YOUR_API_KEY")

   # Get food by FDC ID
   food = client.get_food(1750340)  # Apple, raw, with skin
   
   # Analyze the food
   analysis = analyze_food(
       food,
       dri_type=DriType.RDA,
       gender=Gender.MALE,
       serving_size=100.0
   )
   
   # Print analysis results
   print(f"Calories: {analysis.calories_per_serving:.1f} kcal")
   
   # Print macronutrient distribution
   for macro, percent in analysis.macronutrient_distribution.items():
       print(f"{macro.capitalize()}: {percent:.1f}%")

Compare Foods
^^^^^^^^^^

The ``04_compare_foods.py`` example shows how to compare the nutrient content of multiple foods:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.analysis import compare_foods

   # Initialize the client
   client = FdcClient("YOUR_API_KEY")

   # Get foods to compare
   foods = [
       client.get_food(1750340),  # Apple
       client.get_food(1750341),  # Banana
       client.get_food(1750342)   # Orange
   ]
   
   # Compare the foods
   comparison = compare_foods(
       foods,
       nutrient_ids=["vitamin_c", "potassium", "fiber"]
   )
   
   # Print comparison results
   for nutrient_id, values in comparison.items():
       print(f"\n{nutrient_id.capitalize()}:")
       for food_name, amount, unit in values:
           print(f"- {food_name}: {amount:.1f} {unit}")

Recipe Analysis
^^^^^^^^^^^

The ``05_recipe_analysis.py`` example demonstrates how to create and analyze recipes:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.analysis.recipe import create_recipe, analyze_recipe

   # Initialize the client
   client = FdcClient("YOUR_API_KEY")

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
   
   # Print analysis results
   per_serving = analysis.per_serving_analysis
   print(f"Calories per serving: {per_serving.calories_per_serving:.1f} kcal")

Advanced Examples
--------------

Django Integration
^^^^^^^^^^^^^

The ``06_django_integration.py`` example shows how to use the library with Django for caching API responses:

.. code-block:: python

   from usda_fdc.django import FdcCache

   # Initialize the cache
   cache = FdcCache(api_key="YOUR_API_KEY")

   # Search and cache results
   results = cache.search("banana")
   
   # Get food from cache or API
   food = cache.get_food(1750340)

Advanced Analysis
^^^^^^^^^^^^^

The ``07_advanced_analysis.py`` example demonstrates advanced nutrient analysis features:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.analysis import analyze_food, DriType, Gender

   # Initialize the client
   client = FdcClient("YOUR_API_KEY")

   # Get food by FDC ID
   food = client.get_food(1750340)  # Apple, raw, with skin
   
   # Analyze the food with different DRI types
   rda_analysis = analyze_food(food, dri_type=DriType.RDA)
   ai_analysis = analyze_food(food, dri_type=DriType.AI)
   ul_analysis = analyze_food(food, dri_type=DriType.UL)
   
   # Compare DRI percentages
   for nutrient_id in ["vitamin_c", "calcium", "iron"]:
       print(f"\n{nutrient_id.capitalize()}:")
       for analysis, dri_type in [(rda_analysis, "RDA"), (ai_analysis, "AI"), (ul_analysis, "UL")]:
           nutrient_value = analysis.get_nutrient(nutrient_id)
           if nutrient_value and nutrient_value.dri_percent is not None:
               print(f"- {dri_type}: {nutrient_value.dri_percent:.1f}%")

Command-Line Interface
^^^^^^^^^^^^^^^^^

The ``08_analyze_version.py`` example shows how to use the nutrient analysis command-line interface:

.. code-block:: python

   import subprocess

   # Run the fdc-nat command
   subprocess.run(["fdc-nat", "analyze", "1750340", "--serving-size", "100"])
   
   # Compare multiple foods
   subprocess.run([
       "fdc-nat", "compare", "1750340", "1750341", "1750342",
       "--nutrients", "vitamin_c,potassium,fiber"
   ])

Meal Planning
^^^^^^^^^^^

The ``09_meal_planning.py`` example demonstrates how to create and analyze a meal plan:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.analysis.recipe import create_recipe, analyze_recipe

   # Initialize the client
   client = FdcClient("YOUR_API_KEY")

   # Create breakfast recipe
   breakfast = create_recipe(
       name="Healthy Breakfast",
       ingredient_texts=[
           "1 cup oatmeal, cooked",
           "1 medium banana",
           "1 cup milk, 1% fat",
           "1 tbsp honey",
           "2 tbsp almonds, sliced"
       ],
       client=client,
       servings=1
   )
   
   # Create lunch recipe
   lunch = create_recipe(
       name="Chicken Salad",
       ingredient_texts=[
           "3 oz grilled chicken breast",
           "2 cups mixed greens",
           "1/4 cup cherry tomatoes",
           "1/4 cup cucumber, sliced",
           "1 tbsp olive oil",
           "1 tbsp balsamic vinegar"
       ],
       client=client,
       servings=1
   )
   
   # Analyze recipes
   breakfast_analysis = analyze_recipe(breakfast)
   lunch_analysis = analyze_recipe(lunch)
   
   # Calculate daily totals
   total_calories = (breakfast_analysis.per_serving_analysis.calories_per_serving + 
                    lunch_analysis.per_serving_analysis.calories_per_serving)
   
   print(f"Total Calories: {total_calories:.1f} kcal")

Visualization
^^^^^^^^^^

The ``10_visualization.py`` example shows how to create visualizations of nutrient data:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.analysis import analyze_food
   from usda_fdc.analysis.visualization import generate_html_report

   # Initialize the client
   client = FdcClient("YOUR_API_KEY")

   # Get and analyze a food
   food = client.get_food(1750340)  # Apple, raw, with skin
   analysis = analyze_food(food)
   
   # Generate HTML report
   html_report = generate_html_report(analysis)
   
   # Save the report to a file
   with open("report.html", "w") as f:
       f.write(html_report)

Running the Examples
-----------------

To run the examples, make sure you have:

1. Installed the library: ``pip install usda-fdc`` or ``pip install -e .`` from the repository root
2. Set your FDC API key as an environment variable: ``export FDC_API_KEY=your_api_key_here``

Alternatively, you can create a ``.env`` file in the examples directory with the following content:

.. code-block:: ini

   FDC_API_KEY=your_api_key_here

Then run the examples:

.. code-block:: bash

   python examples/01_basic_search.py