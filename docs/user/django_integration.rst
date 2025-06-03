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
   results = cache.search("banana")
   
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

The admin interface provides:

- List views with filtering by data type, brand, and category
- Detail views with nutrient information
- Bulk actions for refreshing foods from the API
- Custom filters for finding foods by nutrient content

Management Commands
----------------

The library includes Django management commands for importing and refreshing data:

.. code-block:: bash

   # Import a specific food by FDC ID
   python manage.py fdc_import --fdc-id 1750340
   
   # Import foods matching a search query
   python manage.py fdc_import --search "apple" --limit 50
   
   # Import foods of specific data types
   python manage.py fdc_import --data-type "Branded" "Foundation" --limit 100
   
   # Refresh stale foods (not updated in 30 days)
   python manage.py fdc_refresh --stale --days 30 --limit 500
   
   # Warm the cache with new foods
   python manage.py fdc_refresh --warm --data-type "Branded" --limit 1000

Background Tasks
-------------

For large datasets, you can use background tasks to cache data:

.. code-block:: python

   from usda_fdc.django.tasks import refresh_stale_foods, warm_cache
   
   # Refresh foods that haven't been updated in 30 days
   refresh_stale_foods(days=30, limit=1000)
   
   # Warm the cache with new foods
   warm_cache(data_type=["Branded"], limit=1000, batch_size=20)

The tasks module is designed to work with Celery, Django Q, or other task queues:

.. code-block:: python

   # With Celery
   from celery import shared_task
   
   @shared_task
   def refresh_stale_foods_task():
       from usda_fdc.django.tasks import refresh_stale_foods
       refresh_stale_foods(days=30, limit=1000)
   
   # With Django Q
   from django_q.tasks import async_task
   
   async_task(
       'usda_fdc.django.tasks.refresh_stale_foods',
       days=30,
       limit=1000
   )

Views and URLs
-----------

The library includes Django views and URL patterns for displaying food data:

.. code-block:: python

   # urls.py
   from django.urls import include, path
   
   urlpatterns = [
       # ...
       path('usda/', include('usda_fdc.django.urls')),
       # ...
   ]

This provides the following URLs:

- ``/usda/foods/`` - List view of foods with search and filtering
- ``/usda/foods/<fdc_id>/`` - Detail view of a specific food
- ``/usda/api/foods/<fdc_id>/`` - JSON API endpoint for a specific food