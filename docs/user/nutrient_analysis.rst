Nutrient Analysis
================

The USDA FDC library includes a comprehensive nutrient analysis module that allows you to analyze the nutrient content of foods, compare foods, and analyze recipes.

Basic Usage
----------

To analyze a food, use the ``analyze_food`` function:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.analysis import analyze_food, DriType, Gender
   
   # Initialize the client
   client = FdcClient("YOUR_API_KEY")
   
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
   print(f"Vitamin C: {analysis.get_nutrient('vitamin_c').amount} mg")

Comparing Foods
-------------

You can compare the nutrient content of multiple foods:

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
       nutrient_ids=["vitamin_c", "potassium", "fiber"],
       serving_sizes=[100.0, 100.0, 100.0]
   )
   
   # Print the comparison
   for nutrient_id, values in comparison.items():
       print(f"{nutrient_id}:")
       for food, amount, unit in values:
           print(f"  {food}: {amount} {unit}")

Recipe Analysis
------------

The library also supports recipe analysis:

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
           "100g strawberries",
           "50g blueberries"
       ],
       client=client,
       servings=2
   )
   
   # Analyze the recipe
   analysis = analyze_recipe(
       recipe,
       dri_type=DriType.RDA,
       gender=Gender.MALE
   )
   
   # Access the analysis results
   per_serving = analysis.per_serving_analysis
   print(f"Calories per serving: {per_serving.calories_per_serving} kcal")

Dietary Reference Intakes
-----------------------

The library includes Dietary Reference Intakes (DRI) data, including Recommended Dietary Allowances (RDA) and Tolerable Upper Intake Levels (UL):

.. code-block:: python

   from usda_fdc.analysis.dri import get_dri, DriType, Gender
   
   # Get the RDA for vitamin C for males
   vitamin_c_rda = get_dri("vitamin_c", DriType.RDA, Gender.MALE)
   print(f"Vitamin C RDA for males: {vitamin_c_rda * 1000} mg")
   
   # Get the UL for vitamin C
   vitamin_c_ul = get_dri("vitamin_c", DriType.UL)
   print(f"Vitamin C UL: {vitamin_c_ul * 1000} mg")

Visualization
-----------

The library includes visualization tools for generating charts and reports:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.analysis import analyze_food
   from usda_fdc.analysis.visualization import generate_html_report
   
   # Initialize the client
   client = FdcClient("YOUR_API_KEY")
   
   # Get a food
   food = client.get_food(1750340)  # Apple, raw, with skin
   
   # Analyze the food
   analysis = analyze_food(food)
   
   # Generate an HTML report
   html = generate_html_report(analysis)
   
   # Save the report to a file
   with open("food_analysis.html", "w") as f:
       f.write(html)

Command-Line Interface
-------------------

The library includes a command-line interface for nutrient analysis:

.. code-block:: bash

   # Analyze a food
   fdc-analyze 1750340 --serving-size 100 --format html --output apple.html
   
   # Compare foods
   fdc-analyze compare 1750340 1750341 1750342 --nutrients vitamin_c,potassium,fiber
   
   # Analyze a recipe
   fdc-analyze recipe --name "Fruit Salad" --ingredients "1 apple" "1 banana" "100g strawberries"

Examples
-------

The library includes example scripts in the ``usda_fdc.analysis.examples`` package:

.. code-block:: python

   # Run the analyze_food example
   from usda_fdc.analysis.examples import analyze_food
   analyze_food.main()
   
   # Run the compare_foods example
   from usda_fdc.analysis.examples import compare_foods
   compare_foods.main()
   
   # Run the recipe_analysis example
   from usda_fdc.analysis.examples import recipe_analysis
   recipe_analysis.main()