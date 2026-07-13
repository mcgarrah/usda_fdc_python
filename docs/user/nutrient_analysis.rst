Nutrient Analysis
================

The USDA FDC Python Client includes a comprehensive nutrient analysis module that allows you to:

- Analyze the nutrient content of foods
- Compare nutrients across multiple foods
- Create and analyze recipes
- Generate visualizations and reports

Basic Nutrient Analysis
---------------------

To analyze the nutrient content of a food:

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
       serving_size=100.0,  # in grams
       dri_type=DriType.RDA,
       gender=Gender.MALE,
       age=30
   )

   # Access the analysis results
   print(f"Calories: {analysis.calories_per_serving:.1f} kcal")
   
   # Print macronutrient distribution
   for macro, percent in analysis.macronutrient_distribution.items():
       print(f"- {macro.capitalize()}: {percent:.1f}%")
   
   # Print key nutrients with DRI percentages
   for nutrient_id in ["protein", "fiber", "vitamin_c"]:
       nutrient_value = analysis.get_nutrient(nutrient_id)
       if nutrient_value:
           dri_percent = f"{nutrient_value.dri_percent:.1f}%" if nutrient_value.dri_percent is not None else "N/A"
           print(f"- {nutrient_value.nutrient.name}: {nutrient_value.amount:.1f} {nutrient_value.unit} ({dri_percent} of DRI)")

Comparing Foods
------------

To compare the nutrient content of multiple foods:

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

Recipe Analysis
------------

The library includes a recipe analysis module that allows you to:

- Create recipes from ingredient descriptions
- Analyze the nutrient content of recipes
- Calculate per-serving nutritional information

Creating and Analyzing Recipes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

   # Access the analysis results
   per_serving = analysis.per_serving_analysis
   print(f"Recipe: {recipe.name}")
   print(f"Servings: {recipe.servings}")
   print(f"Weight per serving: {recipe.get_weight_per_serving():.1f}g")
   print(f"Calories per serving: {per_serving.calories_per_serving:.1f} kcal")
   print(f"Protein per serving: {per_serving.get_nutrient('protein').amount:.1f} g")

Working with Ingredients
^^^^^^^^^^^^^^^^^^^^

The recipe module can parse ingredient descriptions and estimate weights:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.analysis.recipe import parse_ingredient

   # Initialize the client
   client = FdcClient("YOUR_API_KEY")

   # Parse an ingredient
   ingredient = parse_ingredient("1 cup flour", client)
   
   print(f"Food: {ingredient.food.description}")
   print(f"Weight: {ingredient.weight_g:.1f}g")

Visualization
-----------

The library includes tools for visualizing nutrient data:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.analysis import analyze_food
   from usda_fdc.analysis.visualization import generate_html_report

   # Initialize the client
   client = FdcClient("YOUR_API_KEY")

   # Get and analyze a food
   food = client.get_food(1750340)
   analysis = analyze_food(food)

   # Generate HTML report
   html = generate_html_report(analysis)
   with open("report.html", "w") as f:
       f.write(html)

The HTML report includes:

- Basic food information
- Macronutrient distribution chart
- Nutrient content compared to DRIs
- Detailed nutrient table

Dietary Reference Intakes (DRIs)
-----------------------------

The library ships Dietary Reference Intake data drawn from the Institute of
Medicine's *Dietary Reference Intakes: The Essential Guide to Nutrient
Requirements* (2006).

.. code-block:: python

   from usda_fdc.analysis.dri import get_dri_value, DriType, Gender

   # Get the RDA for protein for a 30-year-old male
   protein_rda = get_dri_value(
       nutrient_id="protein",
       dri_type=DriType.RDA,
       gender=Gender.MALE,
       age=30
   )

   print(f"Protein RDA: {protein_rda.value}{protein_rda.unit}")   # 56g

Mind the unit. ``get_dri_value`` returns it alongside the number because the
underlying data does not use one scale throughout: iron's RDA is ``8`` **mg**
while its UL is ``0.045`` **g**. Comparing a food's milligrams against the
latter would overstate it a thousandfold. ``analyze_food`` converts the food's
amount into the DRI's unit before working out ``dri_percent``, and reports no
percentage at all where the two cannot be compared — vitamin A in IU against a
µg allowance, for instance.

``get_dri`` still returns the bare number, in whatever unit that DRI type's data
uses.

Available DRI types:

- ``DriType.RDA``: Recommended Dietary Allowance — **data included**
- ``DriType.UL``: Tolerable Upper Intake Level — **data included**
- ``DriType.AI``: Adequate Intake — no data; lookups return ``None``
- ``DriType.EAR``: Estimated Average Requirement — no data; lookups return ``None``
- ``DriType.AMDR``: Acceptable Macronutrient Distribution Range — no data; lookups return ``None``

Asking for a type with no data behind it logs a warning once and returns
``None``, so an empty DRI column has a stated reason rather than being a
mystery.

Command-Line Interface
-------------------

The library includes a command-line interface for nutrient analysis:

.. code-block:: bash

   # Analyze a food
   fdc-nat analyze 1750340 --serving-size 100

   # Compare multiple foods
   fdc-nat compare 1750340 1750341 1750342 --nutrients vitamin_c,potassium,fiber

   # Analyze a recipe
   fdc-nat recipe --name "Fruit Salad" --ingredients "1 apple" "1 banana" "100g strawberries"

   # Generate HTML report
   fdc-nat analyze 1750340 --format html --output report.html

See the :doc:`cli` page for more details on the command-line interface.