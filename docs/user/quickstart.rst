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

Command Line Interface
--------------------

The package includes a command-line tool called ``fdc`` that provides quick access to common operations:

.. code-block:: bash

   # Search for foods
   fdc search "apple" --page-size 5
   
   # Get food details
   fdc food 1750340
   
   # Get nutrients for a food
   fdc nutrients 1750340
   
   # List foods
   fdc list --page-size 10 --page-number 1

For more details on the CLI, see :doc:`cli`.

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