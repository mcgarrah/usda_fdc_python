Testing
=======

This document provides information about testing the USDA FDC Python Client.

Test Framework
------------

This project uses pytest for testing. The tests are located in the ``tests/`` directory.

Running Tests
-----------

To run the tests, use the following command:

.. code-block:: bash

   pytest

To run tests with coverage:

.. code-block:: bash

   pytest --cov=usda_fdc

To generate a coverage report:

.. code-block:: bash

   pytest --cov=usda_fdc --cov-report=html

The coverage report will be available in the ``htmlcov/`` directory.

Test Structure
------------

The tests are organized as follows:

- ``tests/unit/``: Unit tests for individual components
- ``tests/integration/``: Integration tests that interact with the API
- ``tests/django/``: Tests for Django integration

Writing Tests
-----------

When writing tests, follow these guidelines:

1. Create a new test file for each module or class being tested.
2. Use descriptive test names that explain what is being tested.
3. Use fixtures to set up test data and mock external dependencies.
4. Test both success and failure cases.

Example Test
----------

Here's an example of a test for the ``FdcClient`` class:

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
   
   def test_search_api_error(client):
       with patch.object(client, "_make_request", side_effect=FdcApiError("API error")):
           with pytest.raises(FdcApiError):
               client.search("test")

Mocking
------

For unit tests, use the ``unittest.mock`` module to mock external dependencies:

.. code-block:: python

   from unittest.mock import patch, MagicMock
   
   @patch("requests.Session.request")
   def test_make_request(mock_request, client):
       mock_response = MagicMock()
       mock_response.status_code = 200
       mock_response.json.return_value = {"key": "value"}
       mock_request.return_value = mock_response
       
       result = client._make_request("endpoint")
       
       assert result == {"key": "value"}
       mock_request.assert_called_once()

Integration Tests
---------------

Integration tests interact with the actual API. To run these tests, you need a valid API key:

.. code-block:: bash

   # Set API key for integration tests
   export FDC_API_KEY=your_api_key_here
   
   # Run integration tests
   pytest tests/integration/

These tests are marked with the ``integration`` marker and are skipped by default. To run them:

.. code-block:: bash

   pytest -m integration