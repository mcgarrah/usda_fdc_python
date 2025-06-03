Configuration
=============

Environment Variables
-------------------

The USDA FDC client can be configured using environment variables:

.. code-block:: bash

   # Required
   FDC_API_KEY=your_api_key_here
   
   # Optional
   FDC_API_URL=https://api.nal.usda.gov/fdc/v1
   FDC_CACHE_ENABLED=True
   FDC_CACHE_TIMEOUT=86400

You can set these variables in your environment or use a ``.env`` file with the ``python-dotenv`` package.

.env File
--------

Create a ``.env`` file in your project root:

.. code-block:: bash

   FDC_API_KEY=your_api_key_here
   FDC_API_URL=https://api.nal.usda.gov/fdc/v1
   FDC_CACHE_ENABLED=True
   FDC_CACHE_TIMEOUT=86400

Then load it in your code:

.. code-block:: python

   from dotenv import load_dotenv
   
   load_dotenv()  # Load variables from .env file

Client Configuration
------------------

When initializing the client, you can override the default configuration:

.. code-block:: python

   from usda_fdc import FdcClient
   
   # Basic initialization with API key
   client = FdcClient(api_key="your_api_key_here")
   
   # Custom API URL
   client = FdcClient(
       api_key="your_api_key_here",
       base_url="https://custom-api-url.example.com"
   )

Django Settings
-------------

When using the Django integration, you can configure the client in your Django settings:

.. code-block:: python

   # settings.py
   
   FDC_API_KEY = "your_api_key_here"
   FDC_API_URL = "https://api.nal.usda.gov/fdc/v1"
   FDC_CACHE_ENABLED = True
   FDC_CACHE_TIMEOUT = 86400  # 24 hours in seconds

Then use the Django integration:

.. code-block:: python

   from usda_fdc.django import FdcCache
   
   # The cache will automatically use your Django settings
   cache = FdcCache()

CLI Configuration
--------------

The command-line interface can be configured using environment variables or command-line arguments:

.. code-block:: bash

   # Set environment variable
   export FDC_API_KEY=your_api_key_here
   
   # Use the CLI
   fdc search "apple"
   
   # Or provide the API key as an argument
   fdc --api-key your_api_key_here search "apple"