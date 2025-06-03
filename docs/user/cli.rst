Command-Line Interface
=====================

The USDA FDC library includes two command-line interfaces:
- ``fdc`` for accessing the Food Data Central API
- ``fdc-analyze`` for nutrient analysis

FDC Command-Line Interface
------------------------

The ``fdc`` command provides quick access to food data without writing any code.

Basic Usage
~~~~~~~~~

.. code-block:: bash

   fdc [options] <command> [command-options]

Global Options
~~~~~~~~~~~~

.. code-block:: bash

   --api-key KEY       FDC API key (can also be set via FDC_API_KEY environment variable)
   --format FORMAT     Output format: json, pretty, or text (default: pretty)
   --version           Show version and exit
   --help              Show help message and exit

Commands
~~~~~~~

search
^^^^^^

Search for foods using keywords:

.. code-block:: bash

   fdc search "apple" --page-size 10 --page-number 1

food
^^^^

Get detailed information about a specific food:

.. code-block:: bash

   fdc food 1750340

nutrients
^^^^^^^^

Get nutrient information for a specific food:

.. code-block:: bash

   fdc nutrients 1750340

list
^^^^

List foods with pagination:

.. code-block:: bash

   fdc list --page-size 10 --page-number 1

Nutrient Analysis Command-Line Interface
-------------------------------------

The ``fdc-analyze`` command provides tools for analyzing nutrient content.

Basic Usage
~~~~~~~~~

.. code-block:: bash

   fdc-analyze [options] <command> [command-options]

Global Options
~~~~~~~~~~~~

.. code-block:: bash

   --api-key KEY       FDC API key (can also be set via FDC_API_KEY environment variable)
   --help              Show help message and exit

Commands
~~~~~~~

analyze
^^^^^^^

Analyze a food:

.. code-block:: bash

   fdc-analyze analyze 1750340 --serving-size 100 --format html --output apple.html

Options:

.. code-block:: bash

   --serving-size SIZE    Serving size in grams (default: 100)
   --dri-type TYPE        DRI type to use: rda or ul (default: rda)
   --gender GENDER        Gender to use: male or female (default: male)
   --format FORMAT        Output format: text, json, or html (default: text)
   --output FILE          Output file for HTML format (default: stdout)

compare
^^^^^^^

Compare multiple foods:

.. code-block:: bash

   fdc-analyze compare 1750340 1750341 1750342 --nutrients vitamin_c,potassium,fiber

Options:

.. code-block:: bash

   --nutrients LIST       Comma-separated list of nutrient IDs to compare
   --serving-size SIZE    Serving size in grams (default: 100)
   --format FORMAT        Output format: text or json (default: text)

recipe
^^^^^^

Analyze a recipe:

.. code-block:: bash

   fdc-analyze recipe --name "Fruit Salad" --ingredients "1 apple" "1 banana" "100g strawberries"

Options:

.. code-block:: bash

   --name NAME            Name of the recipe (default: Recipe)
   --ingredients LIST     Ingredients (e.g., "1 cup flour")
   --ingredients-file FILE File containing ingredients (one per line)
   --servings NUM         Number of servings (default: 1)
   --dri-type TYPE        DRI type to use: rda or ul (default: rda)
   --gender GENDER        Gender to use: male or female (default: male)
   --format FORMAT        Output format: text or json (default: text)

Examples
-------

Search for foods containing "apple":

.. code-block:: bash

   fdc search "apple"

Get detailed information about a specific food:

.. code-block:: bash

   fdc food 1750340

Get nutrient information in JSON format:

.. code-block:: bash

   fdc nutrients 1750340 --format json

List only branded foods:

.. code-block:: bash

   fdc list --data-type "Branded"

Analyze a food and generate an HTML report:

.. code-block:: bash

   fdc-analyze analyze 1750340 --format html --output apple.html

Compare the vitamin C content of different fruits:

.. code-block:: bash

   fdc-analyze compare 1750340 1750341 1750342 --nutrients vitamin_c

Analyze a recipe from a file:

.. code-block:: bash

   fdc-analyze recipe --name "Fruit Salad" --ingredients-file ingredients.txt

Using Environment Variables
------------------------

You can set the API key using an environment variable:

.. code-block:: bash

   export FDC_API_KEY=your_api_key_here
   fdc search "apple"

Or using a .env file in your current directory:

.. code-block:: bash

   # .env file
   FDC_API_KEY=your_api_key_here

   # Then run
   fdc search "apple"