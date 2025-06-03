Command-Line Interface
=====================

The USDA FDC library includes a command-line interface (CLI) that provides quick access to food data without writing any code.

Installation
-----------

The CLI is automatically installed when you install the package:

.. code-block:: bash

   pip install usda-fdc

Basic Usage
---------

The main command is ``fdc``, followed by a subcommand:

.. code-block:: bash

   fdc [options] <command> [command-options]

Global Options
------------

The following options apply to all commands:

.. code-block:: bash

   --api-key KEY       FDC API key (can also be set via FDC_API_KEY environment variable)
   --format FORMAT     Output format: json, pretty, or text (default: pretty)
   --version           Show version and exit
   --help              Show help message and exit

Commands
-------

search
~~~~~~

Search for foods using keywords:

.. code-block:: bash

   fdc search "apple" --page-size 10 --page-number 1

Options:

.. code-block:: bash

   --data-type TYPE    Filter by data type (can be specified multiple times)
   --page-size SIZE    Results per page (default: 10)
   --page-number NUM   Page number (default: 1)

food
~~~~

Get detailed information about a specific food:

.. code-block:: bash

   fdc food 1750340

nutrients
~~~~~~~~

Get nutrient information for a specific food:

.. code-block:: bash

   fdc nutrients 1750340

list
~~~~

List foods with pagination:

.. code-block:: bash

   fdc list --page-size 10 --page-number 1

Options:

.. code-block:: bash

   --data-type TYPE    Filter by data type (can be specified multiple times)
   --page-size SIZE    Results per page (default: 10)
   --page-number NUM   Page number (default: 1)

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