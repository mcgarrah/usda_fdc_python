"""
Advanced unit tests for the FdcClient class.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from usda_fdc import FdcClient, FdcApiError

def test_environment_variable_loading():
    """Test loading API key from environment variables."""
    import os
    from usda_fdc import FdcClient
    
    # Save original environment variable
    original_key = os.environ.get("FDC_API_KEY")
    
    try:
        # Set test environment variable
        os.environ["FDC_API_KEY"] = "test_env_key"
        
        # Create client without explicit API key
        client = FdcClient()
        
        # Verify it used the environment variable
        assert client.api_key == "test_env_key"
    finally:
        # Restore original environment
        if original_key:
            os.environ["FDC_API_KEY"] = original_key
        else:
            if "FDC_API_KEY" in os.environ:
                del os.environ["FDC_API_KEY"]

def test_missing_api_key():
    """Test error when no API key is provided."""
    import os
    from usda_fdc import FdcClient
    
    # Save original environment variable
    original_key = os.environ.get("FDC_API_KEY")
    
    try:
        # Remove environment variable
        if "FDC_API_KEY" in os.environ:
            del os.environ["FDC_API_KEY"]
        
        # Patch load_dotenv to return False (no .env file loaded)
        with patch('usda_fdc.client.load_dotenv', return_value=False):
            # Attempt to create client without API key
            with pytest.raises(ValueError) as excinfo:
                FdcClient()
            
            assert "No API key provided" in str(excinfo.value)
    finally:
        # Restore original environment
        if original_key:
            os.environ["FDC_API_KEY"] = original_key

def test_dotenv_loading():
    """Test loading API key from .env file."""
    import os
    import tempfile
    from usda_fdc import FdcClient
    
    # Save original environment variable
    original_key = os.environ.get("FDC_API_KEY")
    
    try:
        # Remove environment variable
        if "FDC_API_KEY" in os.environ:
            del os.environ["FDC_API_KEY"]
        
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
            temp.write('FDC_API_KEY=test_dotenv_key')
            env_path = temp.name
        
        # Create client with dotenv loading
        with patch('usda_fdc.client.load_dotenv', return_value=True) as mock_load_dotenv:
            with patch.dict('os.environ', {'FDC_API_KEY': 'test_dotenv_key'}):
                client = FdcClient()
                assert client.api_key == "test_dotenv_key"
                mock_load_dotenv.assert_called_once()
    finally:
        # Cleanup
        if os.path.exists(env_path):
            os.unlink(env_path)
        if original_key:
            os.environ["FDC_API_KEY"] = original_key