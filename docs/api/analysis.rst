Analysis API
===========

.. module:: usda_fdc.analysis

The analysis module provides tools for analyzing nutrient content, comparing to dietary reference intakes, and calculating nutritional information for recipes.

Nutrient Analysis
---------------

.. autoclass:: usda_fdc.analysis.analysis.NutrientAnalysis
   :members:

.. autoclass:: usda_fdc.analysis.analysis.NutrientValue
   :members:

.. autofunction:: usda_fdc.analysis.analysis.analyze_food

.. autofunction:: usda_fdc.analysis.analysis.analyze_foods

.. autofunction:: usda_fdc.analysis.analysis.compare_foods

Nutrients
--------

.. module:: usda_fdc.analysis.nutrients

.. autoclass:: Nutrient
   :members:

.. data:: NUTRIENTS
   :annotation: = Dict[str, Nutrient]

   Dictionary of all nutrients by ID.

.. data:: NUTRIENT_GROUPS
   :annotation: = Dict[str, List[str]]

   Dictionary of nutrient groups to lists of nutrient IDs.

Dietary Reference Intakes
-----------------------

.. module:: usda_fdc.analysis.dri

.. autoclass:: DietaryReferenceIntakes
   :members:

.. autoclass:: DriType
   :members:

.. autoclass:: Gender
   :members:

.. autofunction:: get_dri

Recipe Analysis
------------

.. module:: usda_fdc.analysis.recipe

.. autoclass:: Recipe
   :members:

.. autoclass:: Ingredient
   :members:

.. autoclass:: RecipeAnalysis
   :members:

.. autofunction:: parse_ingredient

.. autofunction:: create_recipe

.. autofunction:: analyze_recipe

Visualization
-----------

.. module:: usda_fdc.analysis.visualization

.. autofunction:: generate_macronutrient_chart_data

.. autofunction:: generate_dri_chart_data

.. autofunction:: generate_nutrient_comparison_chart_data

.. autofunction:: generate_nutrient_radar_chart_data

.. autofunction:: generate_html_report

Command-Line Interface
-------------------

.. module:: usda_fdc.analysis.cli

.. autofunction:: main