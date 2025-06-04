Command-Line Interface
====================

The USDA FDC Python Client provides two command-line interfaces:

1. ``fdc`` - The main client interface for accessing FDC data
2. ``fdc-nat`` - The Nutrient Analysis Tool for analyzing foods and recipes

FDC Client CLI
-------------

The ``fdc`` command provides direct access to the USDA FDC API:

.. code-block:: bash

   # Set your API key (or use --api-key parameter)
   export FDC_API_KEY=your_api_key_here

   # Search for foods
   fdc search "apple"

   # Get detailed information for a specific food
   fdc food 1750340

   # Get nutrients for a food
   fdc nutrients 1750340

   # List foods with pagination
   fdc list --page-size 5 --page-number 1

Commands
^^^^^^^^

search
~~~~~~

Search for foods using keywords:

.. code-block:: bash

   fdc search "apple" --data-type Branded --page-size 10

Arguments:

- ``query``: Search query
- ``--data-type``: Filter by data type (e.g., Branded, Foundation)
- ``--page-size``: Results per page (default: 50)
- ``--page-number``: Page number (default: 1)
- ``--sort-by``: Field to sort by
- ``--sort-order``: Sort direction (asc or desc)
- ``--format``: Output format (text, json, pretty)

food
~~~~

Get detailed information for a specific food:

.. code-block:: bash

   fdc food 1750340 --format json

Arguments:

- ``fdc_id``: FDC ID of the food
- ``--format``: Output format (text, json, pretty)

nutrients
~~~~~~~~

Get nutrients for a specific food:

.. code-block:: bash

   fdc nutrients 1750340

Arguments:

- ``fdc_id``: FDC ID of the food
- ``--format``: Output format (text, json, pretty)

list
~~~~

List foods with pagination:

.. code-block:: bash

   fdc list --data-type Foundation --page-size 10

Arguments:

- ``--data-type``: Filter by data type (e.g., Branded, Foundation)
- ``--page-size``: Results per page (default: 50)
- ``--page-number``: Page number (default: 1)
- ``--sort-by``: Field to sort by
- ``--sort-order``: Sort direction (asc or desc)
- ``--format``: Output format (text, json, pretty)

Nutrient Analysis Tool (NAT)
--------------------------

The ``fdc-nat`` command provides tools for analyzing nutrient content and recipes:

.. code-block:: bash

   # Analyze a food
   fdc-nat analyze 1750340 --serving-size 100

   # Compare multiple foods
   fdc-nat compare 1750340 1750341 1750342 --nutrients vitamin_c,potassium,fiber

   # Analyze a recipe
   fdc-nat recipe --name "Fruit Salad" --ingredients "1 apple" "1 banana" "100g strawberries"

   # Generate HTML report
   fdc-nat analyze 1750340 --format html --output report.html

Commands
^^^^^^^^

analyze
~~~~~~~

Analyze the nutrient content of a food:

.. code-block:: bash

   fdc-nat analyze 1750340 --serving-size 100 --dri-type rda --gender male --age 30

Arguments:

- ``fdc_id``: FDC ID of the food
- ``--serving-size``: Serving size in grams (default: 100)
- ``--dri-type``: DRI type (rda, ai, ul, ear, amdr)
- ``--gender``: Gender for DRI (male, female)
- ``--age``: Age for DRI (default: 30)
- ``--detailed``: Show detailed nutrient information
- ``--format``: Output format (text, json, html)
- ``--output``: Output file (default: stdout)

compare
~~~~~~~

Compare the nutrient content of multiple foods:

.. code-block:: bash

   fdc-nat compare 1750340 1750341 1750342 --nutrients vitamin_c,potassium,fiber

Arguments:

- ``fdc_ids``: FDC IDs of the foods to compare
- ``--serving-size``: Serving size in grams (default: 100)
- ``--nutrients``: Comma-separated list of nutrient IDs to compare
- ``--dri-type``: DRI type (rda, ai, ul, ear, amdr)
- ``--gender``: Gender for DRI (male, female)
- ``--age``: Age for DRI (default: 30)
- ``--format``: Output format (text, json)
- ``--output``: Output file (default: stdout)

recipe
~~~~~~

Analyze the nutrient content of a recipe:

.. code-block:: bash

   fdc-nat recipe --name "Fruit Salad" --ingredients "1 apple" "1 banana" "100g strawberries"

Arguments:

- ``--name``: Recipe name (default: Recipe)
- ``--ingredients``: List of ingredients
- ``--ingredients-file``: File with ingredients (one per line)
- ``--servings``: Number of servings (default: 1)
- ``--dri-type``: DRI type (rda, ai, ul, ear, amdr)
- ``--gender``: Gender for DRI (male, female)
- ``--age``: Age for DRI (default: 30)
- ``--detailed``: Show detailed nutrient information
- ``--format``: Output format (text, json, html)
- ``--output``: Output file (default: stdout)

Configuration
-----------

Both command-line tools can be configured using environment variables:

.. code-block:: bash

   # Set API key
   export FDC_API_KEY=your_api_key_here

   # Set API URL (optional)
   export FDC_API_URL=https://api.nal.usda.gov/fdc/v1

You can also use a ``.env`` file in your current directory:

.. code-block:: ini

   FDC_API_KEY=your_api_key_here
   FDC_API_URL=https://api.nal.usda.gov/fdc/v1

Examples
-------

Search for foods containing "apple":

.. code-block:: bash

   fdc search "apple" --page-size 5

Get detailed information for a specific food:

.. code-block:: bash

   fdc food 1750340

Analyze the nutrient content of a food:

.. code-block:: bash

   fdc-nat analyze 1750340 --serving-size 100

Compare the nutrient content of multiple foods:

.. code-block:: bash

   fdc-nat compare 1750340 1750341 1750342 --nutrients vitamin_c,potassium,fiber

Analyze a recipe:

.. code-block:: bash

   fdc-nat recipe --name "Fruit Salad" --ingredients "1 apple" "1 banana" "100g strawberries"

Generate an HTML report:

.. code-block:: bash

   fdc-nat analyze 1750340 --format html --output report.html