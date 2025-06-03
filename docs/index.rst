USDA Food Data Central (FDC) Python Client
=====================================

A comprehensive Python library for interacting with the USDA Food Data Central API, designed for easy integration with Django applications and local database caching.

.. image:: https://readthedocs.org/projects/usda-fdc/badge/?version=latest
   :target: https://usda-fdc.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/usda-fdc.svg
   :target: https://pypi.org/project/usda-fdc/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/usda-fdc.svg
   :target: https://pypi.org/project/usda-fdc/
   :alt: Python Versions

.. image:: https://img.shields.io/pypi/l/usda-fdc.svg
   :target: https://github.com/mcgarrah/usda_fdc_python/blob/main/LICENSE
   :alt: License

Key Features
-----------

* **Complete API Coverage**: Access all endpoints of the USDA FoodData Central API
* **Object-Oriented Interface**: Work with food data using intuitive Python objects
* **Django Integration**: Seamlessly integrate with Django applications
* **Local Database Caching**: Cache API responses for improved performance
* **Command-Line Interface**: Quick access to food data from the terminal
* **Comprehensive Data Models**: Structured models for all FDC data types
* **Unit Conversion**: Convert between different food measurement units
* **Batch Operations**: Efficiently process multiple food items

Installation
-----------

.. code-block:: bash

   pip install usda-fdc

Or install from source:

.. code-block:: bash

   git clone https://github.com/mcgarrah/usda_fdc_python.git
   cd usda_fdc_python
   pip install -e .

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user/installation
   user/quickstart
   user/configuration
   user/django_integration
   user/cli
   user/advanced_usage
   user/error_handling

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/client
   api/models
   api/django
   api/utils
   api/exceptions
   api/cli

.. toctree::
   :maxdepth: 1
   :caption: Development

   dev/contributing
   dev/testing
   dev/releasing

Indices and tables
-----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`