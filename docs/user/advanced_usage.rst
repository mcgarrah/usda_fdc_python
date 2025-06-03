Advanced Usage
=============

This guide covers advanced usage patterns for the USDA FDC Python Client.

Custom API Requests
-----------------

For more control over API requests, you can use the low-level ``_make_request`` method:

.. code-block:: python

   from usda_fdc import FdcClient
   
   client = FdcClient(api_key="your_api_key_here")
   
   # Make a custom request
   data = client._make_request(
       endpoint="foods/search",
       params={
           "query": "apple",
           "pageSize": 25,
           "pageNumber": 1,
           "sortBy": "dataType.keyword",
           "sortOrder": "asc"
       }
   )

Unit Conversion
-------------

The library provides utilities for converting between different measurement units:

.. code-block:: python

   from usda_fdc.utils import convert_measurement, parse_unit_and_value
   
   # Convert between units
   grams = convert_measurement(1, "cup", "g")
   print(f"1 cup = {grams} grams")
   
   # Parse a measurement string
   amount, unit = parse_unit_and_value("2.5 tbsp")
   print(f"Amount: {amount}, Unit: {unit}")
   
   # Convert to grams
   from usda_fdc.utils import convert_to_grams
   
   grams = convert_to_grams(1, "oz")
   print(f"1 oz = {grams} grams")

Batch Processing
--------------

For processing large numbers of food items, use batch operations:

.. code-block:: python

   from usda_fdc import FdcClient
   import time
   
   client = FdcClient(api_key="your_api_key_here")
   
   # Get all food IDs (this could be a large number)
   all_ids = []
   page = 1
   while True:
       foods = client.list_foods(page_size=200, page_number=page)
       if not foods:
           break
       all_ids.extend([food.fdc_id for food in foods])
       page += 1
       time.sleep(1)  # Be nice to the API
   
   print(f"Found {len(all_ids)} food IDs")
   
   # Process in batches of 20 (API limit)
   batch_size = 20
   for i in range(0, len(all_ids), batch_size):
       batch = all_ids[i:i+batch_size]
       foods = client.get_foods(batch)
       print(f"Processed batch {i//batch_size + 1}/{(len(all_ids) + batch_size - 1)//batch_size}")
       time.sleep(1)  # Be nice to the API

Custom Data Processing
-------------------

You can extend the library's data models for custom processing:

.. code-block:: python

   from usda_fdc import FdcClient
   from usda_fdc.models import Food
   
   class EnhancedFood(Food):
       def calculate_calories_per_gram(self):
           for nutrient in self.nutrients:
               if nutrient.name == "Energy" and nutrient.unit_name == "kcal":
                   return nutrient.amount / 100  # per gram
           return 0
       
       def calculate_protein_percentage(self):
           energy = 0
           protein_energy = 0
           
           for nutrient in self.nutrients:
               if nutrient.name == "Energy" and nutrient.unit_name == "kcal":
                   energy = nutrient.amount
               elif nutrient.name == "Protein" and nutrient.unit_name == "g":
                   # Protein has 4 calories per gram
                   protein_energy = nutrient.amount * 4
           
           if energy > 0:
               return (protein_energy / energy) * 100
           return 0
   
   # Use the enhanced class
   client = FdcClient(api_key="your_api_key_here")
   food_data = client.get_food(1750340)
   
   # Convert to enhanced food
   enhanced_food = EnhancedFood(
       fdc_id=food_data.fdc_id,
       description=food_data.description,
       data_type=food_data.data_type,
       nutrients=food_data.nutrients,
       food_portions=food_data.food_portions
   )
   
   print(f"Calories per gram: {enhanced_food.calculate_calories_per_gram()}")
   print(f"Protein percentage: {enhanced_food.calculate_protein_percentage()}%")

Rate Limiting
-----------

To avoid hitting API rate limits, implement a simple rate limiter:

.. code-block:: python

   import time
   from usda_fdc import FdcClient
   
   class RateLimitedClient(FdcClient):
       def __init__(self, api_key, requests_per_minute=10, **kwargs):
           super().__init__(api_key, **kwargs)
           self.requests_per_minute = requests_per_minute
           self.interval = 60 / requests_per_minute
           self.last_request_time = 0
       
       def _make_request(self, endpoint, method="GET", params=None, data=None):
           # Wait if needed
           current_time = time.time()
           time_since_last = current_time - self.last_request_time
           
           if time_since_last < self.interval:
               time.sleep(self.interval - time_since_last)
           
           # Make the request
           result = super()._make_request(endpoint, method, params, data)
           
           # Update last request time
           self.last_request_time = time.time()
           
           return result
   
   # Use the rate-limited client
   client = RateLimitedClient(
       api_key="your_api_key_here",
       requests_per_minute=5  # Maximum 5 requests per minute
   )