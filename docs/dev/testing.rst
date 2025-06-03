Testing
=======

This document provides information about testing the USDA FDC Python Client.

Test Framework
------------

This project uses pytest for testing. The tests are located in the ``tests/`` directory and are organized into three categories:

- **Unit Tests**: Tests for individual components without external dependencies
- **Integration Tests**: Tests that interact with the actual USDA FDC API
- **Django Tests**: Tests for Django integration features

Running Tests
-----------

To run the tests, first install the development dependencies:

.. code-block:: bash

   pip install -e ".[dev]"

Or using the requirements file:

.. code-block:: bash

   pip install -r requirements-dev.txt

Then run the tests using pytest:

.. code-block:: bash

   # Run all unit tests (default)
   pytest

   # Run specific test categories
   pytest tests/unit
   pytest -m integration
   pytest -m django

   # Run all tests
   pytest -m "integration or django or not integration"

   # Run with coverage
   pytest --cov=usda_fdc
   pytest --cov=usda_fdc --cov-report=html

Integration Tests
---------------

Integration tests interact with the actual USDA FDC API and require a valid API key:

.. code-block:: bash

   # Set API key for integration tests
   export FDC_API_KEY=your_api_key_here
   
   # Run integration tests
   pytest -m integration

These tests are marked with the ``integration`` marker and are skipped by default.

Django Tests
----------

Django tests require Django to be installed and are marked with the ``django`` marker:

.. code-block:: bash

   # Install Django dependencies
   pip install -e ".[django]"
   
   # Run Django tests
   pytest -m django

These tests are skipped automatically if Django is not installed.

VS Code Integration
----------------

If you're using Visual Studio Code, the repository includes configuration files for running tests:

1. **Debug Configurations**:
   - Python: All Tests
   - Python: Unit Tests
   - Python: Integration Tests
   - Python: Django Tests

2. **Tasks**:
   - Run All Tests
   - Run Unit Tests
   - Run Integration Tests
   - Run Django Tests
   - Run Tests with Coverage

To use these configurations, open the Command Palette (Ctrl+Shift+P) and select "Tasks: Run Task" or "Debug: Select and Start Debugging".

Test Structure
------------

The tests are organized as follows:

- ``tests/unit/``: Unit tests for individual components
- ``tests/integration/``: Integration tests that interact with the API
- ``tests/django/``: Tests for Django integration
- ``tests/conftest.py``: Shared fixtures and test utilities

Writing Tests
-----------

When writing tests, follow these guidelines:

1. Create a new test file for each module or class being tested.
2. Use descriptive test names that explain what is being tested.
3. Use fixtures to set up test data and mock external dependencies.
4. Test both success and failure cases.
5. Mark integration tests with ``@pytest.mark.integration``.
6. Mark Django tests with ``@pytest.mark.django``.

Example Test
----------

Here's an example of a unit test for the ``FdcClient`` class:

.. code-block:: python

   import pytest
   from unittest.mock import patch, MagicMock
   from usda_fdc import FdcClient, FdcApiError
   
   @pytest.fixture
   def client():
       return FdcClient(api_key="test_key")
   
   def test_search_success(client):
       # Mock the API response
       mock_response = {
           "totalHits": 1,
           "currentPage": 1,
           "totalPages": 1,
           "foods": [
               {
                   "fdcId": 1234,
                   "description": "Test Food",
                   "dataType": "Branded"
               }
           ]
       }
       
       with patch.object(client, "_make_request", return_value=mock_response):
           result = client.search("test")
           
           assert result.total_hits == 1
           assert len(result.foods) == 1
           assert result.foods[0].fdc_id == 1234
           assert result.foods[0].description == "Test Food"