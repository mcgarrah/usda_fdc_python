Django Integration
=================

The USDA FDC library provides seamless integration with Django applications, allowing you to cache API responses in your database and use Django's ORM to query food data.

Setup
-----

1. Install the package with Django dependencies:

   .. code-block:: bash

      pip install usda-fdc[django]

2. Add the Django app to your ``INSTALLED_APPS`` in ``settings.py``:

   .. code-block:: python

      INSTALLED_APPS = [
          # ...
          'usda_fdc.django',
          # ...
      ]

3. Configure the FDC client in your Django settings:

   .. code-block:: python

      # USDA FDC settings
      FDC_API_KEY = "your_api_key_here"
      FDC_API_URL = "https://api.nal.usda.gov/fdc/v1"
      FDC_CACHE_ENABLED = True
      FDC_CACHE_TIMEOUT = 86400  # 24 hours in seconds

4. Run migrations to create the necessary database tables:

   .. code-block:: bash

      python manage.py migrate

Using the Cache
-------------

The ``FdcCache`` class provides a caching layer that stores API responses in both Django models and Django's cache:

.. code-block:: python

   from usda_fdc.django import FdcCache
   
   # Initialize the cache
   cache = FdcCache()
   
   # Search for foods (results will be cached)
   results = cache.search("apple")
   
   # Get a food by FDC ID (will be cached in database)
   food = cache.get_food(1750340)
   
   # Get multiple foods (will use database cache when available)
   foods = cache.get_foods([1750340, 1750341, 1750342])
   
   # Force refresh from API
   food = cache.get_food(1750340, force_refresh=True)

Django Models
-----------

The library provides Django models that mirror the FDC data structures:

.. code-block:: python

   from usda_fdc.django.models import FoodModel, NutrientModel
   
   # Query foods directly using Django's ORM
   branded_foods = FoodModel.objects.filter(data_type="Branded")
   
   # Get foods with specific nutrients
   high_protein = NutrientModel.objects.filter(
       name="Protein",
       amount__gt=20
   ).select_related('food')
   
   for nutrient in high_protein:
       print(f"{nutrient.food.description}: {nutrient.amount}g protein")

Admin Integration
--------------

The library includes Django admin integration for managing food data:

.. code-block:: python

   # admin.py
   from django.contrib import admin
   from usda_fdc.django.models import FoodModel, NutrientModel
   
   admin.site.register(FoodModel)
   admin.site.register(NutrientModel)

Background Tasks
-------------

For large datasets, you can use background tasks to cache data:

.. code-block:: python

   from usda_fdc.django import FdcCache
   
   def cache_popular_foods():
       cache = FdcCache()
       popular_ids = [1750340, 1750341, 1750342]  # Example IDs
       cache.get_foods(popular_ids)
   
   # Use with Celery, Django Q, or other task queues
   from django_q.tasks import async_task
   
   async_task(cache_popular_foods)