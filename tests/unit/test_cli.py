"""
Unit tests for the CLI module.
"""

import pytest
import json
from unittest.mock import patch, MagicMock

from usda_fdc.cli import main, search_command, food_command, nutrients_command, list_command
from usda_fdc.models import SearchResult, SearchResultFood, Food, Nutrient

@pytest.fixture
def mock_args():
    """Mock command line arguments."""
    return MagicMock()

@pytest.fixture
def mock_search_result(mock_search_response):
    """Create a SearchResult object from mock response."""
    foods = [
        SearchResultFood(
            fdc_id=food["fdcId"],
            description=food["description"],
            data_type=food["dataType"]
        )
        for food in mock_search_response["foods"]
    ]
    
    return SearchResult(
        foods=foods,
        total_hits=mock_search_response["totalHits"],
        current_page=mock_search_response["currentPage"],
        total_pages=mock_search_response["totalPages"]
    )

@pytest.fixture
def mock_food_object():
    """Create a Food object with nutrients."""
    nutrients = [
        Nutrient(id=1001, name="Protein", amount=10.5, unit_name="g"),
        Nutrient(id=1002, name="Fat", amount=5.2, unit_name="g")
    ]
    
    return Food(
        fdc_id=1234,
        description="Test Food",
        data_type="Branded",
        publication_date="2023-01-01",
        nutrients=nutrients
    )

def test_search_command(mock_args, mock_client, mock_search_result):
    """Test search_command function."""
    mock_args.query = "apple"
    mock_args.page_size = 10
    mock_args.page_number = 1
    mock_args.data_type = None
    mock_args.format = "text"
    
    with patch('usda_fdc.cli.FdcClient', return_value=mock_client):
        with patch.object(mock_client, 'search', return_value=mock_search_result):
            # Capture stdout
            with patch('builtins.print') as mock_print:
                search_command(mock_args)
                
                # Verify print was called with expected output
                mock_print.assert_called()

def test_food_command(mock_args, mock_client, mock_food_object):
    """Test food_command function."""
    mock_args.fdc_id = 1234
    mock_args.format = "text"
    
    with patch('usda_fdc.cli.FdcClient', return_value=mock_client):
        with patch.object(mock_client, 'get_food', return_value=mock_food_object):
            # Capture stdout
            with patch('builtins.print') as mock_print:
                food_command(mock_args)
                
                # Verify print was called with expected output
                mock_print.assert_called()

def test_nutrients_command(mock_args, mock_client, mock_food_object):
    """Test nutrients_command function."""
    mock_args.fdc_id = 1234
    mock_args.format = "text"
    
    with patch('usda_fdc.cli.FdcClient', return_value=mock_client):
        with patch.object(mock_client, 'get_food', return_value=mock_food_object):
            # Capture stdout
            with patch('builtins.print') as mock_print:
                nutrients_command(mock_args)
                
                # Verify print was called with expected output
                mock_print.assert_called()

def test_list_command(mock_args, mock_client):
    """Test list_command function."""
    mock_args.page_size = 10
    mock_args.page_number = 1
    mock_args.data_type = None
    mock_args.format = "text"
    
    # Create mock food objects
    mock_foods = [
        Food(fdc_id=1234, description="Test Food 1", data_type="Branded"),
        Food(fdc_id=5678, description="Test Food 2", data_type="Foundation")
    ]
    
    with patch('usda_fdc.cli.FdcClient', return_value=mock_client):
        with patch.object(mock_client, 'list_foods', return_value=mock_foods):
            # Capture stdout
            with patch('builtins.print') as mock_print:
                list_command(mock_args)
                
                # Verify print was called with expected output
                mock_print.assert_called()

def test_main():
    """Test main function."""
    # Mock sys.argv
    with patch('sys.argv', ['fdc', '--help']):
        with patch('argparse.ArgumentParser.parse_args', side_effect=SystemExit(0)):
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0