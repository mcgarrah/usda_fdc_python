Error Handling
=============

The USDA FDC Python Client provides a comprehensive error handling system to help you handle various error conditions gracefully.

Exception Hierarchy
-----------------

The library defines the following exception hierarchy:

- ``FdcApiError``: Base exception for all API errors
  - ``FdcAuthError``: Authentication failed (invalid API key)
  - ``FdcRateLimitError``: API rate limit exceeded
  - ``FdcValidationError``: Invalid input parameters
  - ``FdcResourceNotFoundError``: Requested resource not found

Basic Error Handling
-----------------

Here's how to handle errors when using the client:

.. code-block:: python

   from usda_fdc import FdcClient, FdcApiError, FdcAuthError, FdcRateLimitError
   
   client = FdcClient(api_key="your_api_key_here")
   
   try:
       food = client.get_food(1750340)
   except FdcAuthError:
       print("Authentication failed. Check your API key.")
   except FdcRateLimitError:
       print("Rate limit exceeded. Try again later.")
   except FdcApiError as e:
       print(f"API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

Handling Specific HTTP Status Codes
--------------------------------

The ``FdcApiError`` exception includes the HTTP status code, which you can use for more specific error handling:

.. code-block:: python

   from usda_fdc import FdcClient, FdcApiError
   
   client = FdcClient(api_key="your_api_key_here")
   
   try:
       food = client.get_food(1750340)
   except FdcApiError as e:
       if hasattr(e, 'status_code'):
           if e.status_code == 404:
               print("Food not found")
           elif e.status_code == 429:
               print("Too many requests. Try again later.")
           elif e.status_code >= 500:
               print("Server error. Try again later.")
           else:
               print(f"API error: {e}")
       else:
           print(f"API error without status code: {e}")

Retry Logic
---------

For transient errors like rate limiting or server errors, you can implement retry logic:

.. code-block:: python

   import time
   from usda_fdc import FdcClient, FdcApiError, FdcRateLimitError
   
   client = FdcClient(api_key="your_api_key_here")
   
   def get_food_with_retry(fdc_id, max_retries=3, retry_delay=5):
       retries = 0
       while retries < max_retries:
           try:
               return client.get_food(fdc_id)
           except FdcRateLimitError:
               retries += 1
               if retries < max_retries:
                   print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                   time.sleep(retry_delay)
                   retry_delay *= 2  # Exponential backoff
               else:
                   raise
           except FdcApiError as e:
               if hasattr(e, 'status_code') and e.status_code >= 500:
                   retries += 1
                   if retries < max_retries:
                       print(f"Server error. Retrying in {retry_delay} seconds...")
                       time.sleep(retry_delay)
                       retry_delay *= 2  # Exponential backoff
                   else:
                       raise
               else:
                   raise
   
   # Use the retry function
   try:
       food = get_food_with_retry(1750340)
   except Exception as e:
       print(f"Failed after retries: {e}")

Logging Errors
------------

It's a good practice to log errors for debugging:

.. code-block:: python

   import logging
   from usda_fdc import FdcClient, FdcApiError
   
   # Configure logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   logger = logging.getLogger('usda_fdc')
   
   client = FdcClient(api_key="your_api_key_here")
   
   try:
       food = client.get_food(1750340)
   except FdcApiError as e:
       logger.error(f"API error when getting food {1750340}: {e}", exc_info=True)
       # Handle the error appropriately
   except Exception as e:
       logger.exception(f"Unexpected error when getting food {1750340}")
       # Handle the error appropriately