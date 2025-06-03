"""Tests for the command-line interface."""

import pytest
from unittest.mock import patch, MagicMock
import argparse
import json

from usda_fdc.cli import (
    main,
    search_command,
    food_command,
    nutrients_command,
    list_command,
    format_output,
    pretty_print_object
)
from usda_fdc.exceptions import FdcApiError


def test_format_output_json(sample_food):
    """Test formatting output as JSON."""
    output = format_output(sample_food, "json")
    # Parse the JSON to ensure it's valid
    data = json.loads(output)
    assert data["fdc_id"] == sample_food.fdc_id
    assert data["description"] == sample_food.description


def test_format_output_pretty(sample_food):
    """Test formatting output as pretty text."""
    output = format_output(sample_food, "pretty")
    assert sample_food.description in output
    assert f"FDC ID: {sample_food.fdc_id}" in output
    assert "Nutrients" in output


def test_format_output_text(sample_food):
    """Test formatting output as plain text."""
    output = format_output(sample_food, "text")
    assert str(sample_food.__dict__) in output


def test_pretty_print_object(sample_food):
    """Test pretty printing an object."""
    output = pretty_print_object(sample_food)
    assert sample_food.description in output
    assert f"FDC ID: {sample_food.fdc_id}" in output
    assert "Type: Branded" in output
    assert "Nutrients" in output
    assert "Portions" in output


def test_search_command(sample_search_result):
    """Test the search command."""
    args = argparse.Namespace(
        api_key="test_key",
        query="apple",
        data_type=None,
        page_size=10,
        page_number=1,
        format="text"
    )
    
    with patch("usda_fdc.cli.FdcClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.search.return_value = sample_search_result
        
        with patch("builtins.print") as mock_print:
            search_command(args)
            
            mock_client_class.assert_called_once_with("test_key")
            mock_client.search.assert_called_once_with(
                query="apple",
                data_type=None,
                page_size=10,
                page_number=1
            )
            
            # Check that print was called with the expected output
            mock_print.assert_any_call(f"Found {sample_search_result.total_hits} results (page {sample_search_result.current_page} of {sample_search_result.total_pages})")


def test_search_command_error():
    """Test the search command with an error."""
    args = argparse.Namespace(
        api_key="test_key",
        query="apple",
        data_type=None,
        page_size=10,
        page_number=1,
        format="text"
    )
    
    with patch("usda_fdc.cli.FdcClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.search.side_effect = FdcApiError("API error")
        
        with patch("builtins.print") as mock_print:
            with pytest.raises(SystemExit):
                search_command(args)
            
            mock_print.assert_called_once_with("Error: API error", file=None)


def test_food_command(sample_food):
    """Test the food command."""
    args = argparse.Namespace(
        api_key="test_key",
        fdc_id="1234",
        format="text"
    )
    
    with patch("usda_fdc.cli.FdcClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_food.return_value = sample_food
        
        with patch("builtins.print") as mock_print:
            food_command(args)
            
            mock_client_class.assert_called_once_with("test_key")
            mock_client.get_food.assert_called_once_with("1234")
            
            # Check that print was called with the expected output
            mock_print.assert_called_once()


def test_nutrients_command(sample_food):
    """Test the nutrients command."""
    args = argparse.Namespace(
        api_key="test_key",
        fdc_id="1234",
        format="text"
    )
    
    with patch("usda_fdc.cli.FdcClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_food.return_value = sample_food
        
        with patch("builtins.print") as mock_print:
            nutrients_command(args)
            
            mock_client_class.assert_called_once_with("test_key")
            mock_client.get_food.assert_called_once_with("1234")
            
            # Check that print was called with the expected output
            if args.format == "json":
                mock_print.assert_called_once()
            else:
                mock_print.assert_any_call(f"Nutrients for {sample_food.description} (FDC ID: {sample_food.fdc_id}):")


def test_list_command(sample_food):
    """Test the list command."""
    args = argparse.Namespace(
        api_key="test_key",
        data_type=["Branded"],
        page_size=10,
        page_number=1,
        format="text"
    )
    
    with patch("usda_fdc.cli.FdcClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.list_foods.return_value = [sample_food, sample_food]
        
        with patch("builtins.print") as mock_print:
            list_command(args)
            
            mock_client_class.assert_called_once_with("test_key")
            mock_client.list_foods.assert_called_once_with(
                data_type=["Branded"],
                page_size=10,
                page_number=1
            )
            
            # Check that print was called with the expected output
            mock_print.assert_any_call(f"Listing 2 foods (page 1):")


@patch("usda_fdc.cli.argparse.ArgumentParser.parse_args")
@patch("usda_fdc.cli.load_dotenv")
def test_main_with_command(mock_load_dotenv, mock_parse_args):
    """Test the main function with a command."""
    args = argparse.Namespace(
        api_key="test_key",
        command="search",
        func=MagicMock()
    )
    mock_parse_args.return_value = args
    
    main()
    
    mock_load_dotenv.assert_called_once()
    args.func.assert_called_once_with(args)


@patch("usda_fdc.cli.argparse.ArgumentParser.parse_args")
@patch("usda_fdc.cli.load_dotenv")
def test_main_without_command(mock_load_dotenv, mock_parse_args):
    """Test the main function without a command."""
    args = argparse.Namespace(
        api_key="test_key",
        command=None
    )
    mock_parse_args.return_value = args
    
    with patch("usda_fdc.cli.argparse.ArgumentParser.print_help") as mock_print_help:
        main()
        
        mock_load_dotenv.assert_called_once()
        mock_print_help.assert_called_once()


@patch("usda_fdc.cli.argparse.ArgumentParser.parse_args")
@patch("usda_fdc.cli.load_dotenv")
def test_main_without_api_key(mock_load_dotenv, mock_parse_args):
    """Test the main function without an API key."""
    args = argparse.Namespace(
        api_key=None,
        command="search"
    )
    mock_parse_args.return_value = args
    
    with patch("builtins.print") as mock_print:
        with pytest.raises(SystemExit):
            main()
        
        mock_load_dotenv.assert_called_once()
        mock_print.assert_called_once_with(
            "Error: No API key provided. Use --api-key or set FDC_API_KEY environment variable.",
            file=None
        )