Installation
============

Requirements
-----------

* Python 3.8 or higher
* ``requests`` library
* ``pint`` library (for unit conversions)
* ``python-dotenv`` library (for loading environment variables)

Installing from PyPI
-------------------

The recommended way to install the USDA FDC Python Client is from PyPI:

.. code-block:: bash

   pip install usda-fdc

This will install the latest stable version of the package along with its dependencies and the ``fdc`` command line tool.

Installing from Source
--------------------

You can also install the package directly from the source code:

.. code-block:: bash

   git clone https://github.com/yourusername/usda_fdc.git
   cd usda_fdc
   pip install -e .

Development Installation
----------------------

If you want to contribute to the development of the package, you can install it with development dependencies:

.. code-block:: bash

   pip install -e ".[dev]"

Or using the requirements files:

.. code-block:: bash

   pip install -r requirements-dev.txt

This will install additional packages needed for development and testing:

* ``pytest`` for running tests
* ``pytest-cov`` for test coverage
* ``black`` for code formatting
* ``isort`` for import sorting
* ``mypy`` for type checking
* ``flake8`` for linting

Django Integration
---------------

To use the Django integration features, install the package with Django dependencies:

.. code-block:: bash

   pip install -e ".[django]"

Or using the requirements file:

.. code-block:: bash

   pip install -r requirements-django.txt

Documentation Installation
------------------------

To build the documentation locally, install the package with documentation dependencies:

.. code-block:: bash

   pip install -e ".[docs]"

Or using the requirements file:

.. code-block:: bash

   pip install -r requirements-docs.txt

Installing All Dependencies
-------------------------

To install all dependencies (development, Django, and documentation), use:

.. code-block:: bash

   pip install -e ".[dev,django,docs]"

Or using the comprehensive requirements file:

.. code-block:: bash

   pip install -r requirements-all.txt