"""
Core client for interacting with the USDA Food Data Central API.
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin

from .exceptions import FdcApiError, FdcRateLimitError, FdcAuthError
from .models import Food, SearchResult, Nutrient

logger = logging.getLogger(__name__)

class FdcClient:
    """
    Client for interacting with the USDA Food Data Central API.
    
    Attributes:
        api_key (str): The API key for authenticating with the FDC API.
        base_url (str): The base URL for the FDC API.
        session (requests.Session): A session object for making HTTP requests.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: str = "https://api.nal.usda.gov/fdc/v1/"
    ):
        """
        Initialize the FDC client.
        
        Args:
            api_key: The API key for authenticating with the FDC API.
                If not provided, will look for FDC_API_KEY environment variable.
            base_url: The base URL for the FDC API.
        
        Raises:
            ValueError: If no API key is provided or found in environment variables.
        """
        self.api_key = api_key or os.environ.get("FDC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key provided. Pass api_key parameter or set FDC_API_KEY environment variable."
            )
        
        self.base_url = base_url
        self.session = requests.Session()
    
    def _make_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        params: Optional[Dict[str, Any]] = None, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the FDC API.
        
        Args:
            endpoint: The API endpoint to request.
            method: The HTTP method to use.
            params: Query parameters to include in the request.
            data: JSON data to include in the request body.
        
        Returns:
            The JSON response from the API.
            
        Raises:
            FdcAuthError: If authentication fails.
            FdcRateLimitError: If the rate limit is exceeded.
            FdcApiError: For other API errors.
        """
        url = urljoin(self.base_url, endpoint)
        
        # Always include the API key in the parameters
        params = params or {}
        params["api_key"] = self.api_key
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data
            )
            
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise FdcAuthError("Authentication failed. Check your API key.") from e
            elif response.status_code == 429:
                raise FdcRateLimitError("Rate limit exceeded.") from e
            else:
                raise FdcApiError(f"API error: {response.status_code} - {response.text}") from e
        except requests.exceptions.RequestException as e:
            raise FdcApiError(f"Request failed: {str(e)}") from e
    
    def search(
        self, 
        query: str, 
        data_type: Optional[List[str]] = None,
        page_size: int = 50,
        page_number: int = 1,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        brand_owner: Optional[str] = None
    ) -> SearchResult:
        """
        Search for foods using keywords.
        
        Args:
            query: One or more search terms.
            data_type: Filter on specific data types (e.g., ["Branded", "Foundation"]).
            page_size: Maximum number of results to return (1-200).
            page_number: Page number to retrieve.
            sort_by: Field to sort by.
            sort_order: Sort direction ("asc" or "desc").
            brand_owner: Filter by brand owner (Branded Foods only).
        
        Returns:
            A SearchResult object containing the search results.
        """
        params = {
            "query": query,
            "pageSize": page_size,
            "pageNumber": page_number
        }
        
        if data_type:
            params["dataType"] = data_type
        if sort_by:
            params["sortBy"] = sort_by
        if sort_order:
            params["sortOrder"] = sort_order
        if brand_owner:
            params["brandOwner"] = brand_owner
        
        data = self._make_request("foods/search", params=params)
        return SearchResult.from_api_data(data)
    
    def get_food(
        self, 
        fdc_id: Union[str, int], 
        format: str = "full", 
        nutrients: Optional[List[int]] = None
    ) -> Food:
        """
        Get detailed information for a specific food by FDC ID.
        
        Args:
            fdc_id: The FDC ID of the food.
            format: The format of the response ("full" or "abridged").
            nutrients: List of up to 25 nutrient numbers to include.
        
        Returns:
            A Food object containing the food data.
        """
        params = {"format": format}
        if nutrients:
            params["nutrients"] = nutrients
        
        data = self._make_request(f"food/{fdc_id}", params=params)
        return Food.from_api_data(data)
    
    def get_foods(
        self, 
        fdc_ids: List[Union[str, int]], 
        format: str = "full", 
        nutrients: Optional[List[int]] = None
    ) -> List[Food]:
        """
        Get detailed information for multiple foods by FDC ID.
        
        Args:
            fdc_ids: List of FDC IDs (max 20).
            format: The format of the response ("full" or "abridged").
            nutrients: List of up to 25 nutrient numbers to include.
        
        Returns:
            A list of Food objects.
        """
        params = {
            "fdcIds": fdc_ids,
            "format": format
        }
        if nutrients:
            params["nutrients"] = nutrients
        
        data = self._make_request("foods", params=params)
        return [Food.from_api_data(item) for item in data]
    
    def get_nutrients(self, fdc_id: Union[str, int]) -> List[Nutrient]:
        """
        Get nutrients for a specific food by FDC ID.
        
        Args:
            fdc_id: The FDC ID of the food.
        
        Returns:
            A list of Nutrient objects.
        """
        food = self.get_food(fdc_id)
        return food.nutrients
    
    def list_foods(
        self,
        data_type: Optional[List[str]] = None,
        page_size: int = 50,
        page_number: int = 1,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None
    ) -> List[Food]:
        """
        Get a paged list of foods.
        
        Args:
            data_type: Filter on specific data types.
            page_size: Maximum number of results to return (1-200).
            page_number: Page number to retrieve.
            sort_by: Field to sort by.
            sort_order: Sort direction ("asc" or "desc").
        
        Returns:
            A list of Food objects.
        """
        params = {
            "pageSize": page_size,
            "pageNumber": page_number
        }
        
        if data_type:
            params["dataType"] = data_type
        if sort_by:
            params["sortBy"] = sort_by
        if sort_order:
            params["sortOrder"] = sort_order
        
        data = self._make_request("foods/list", params=params)
        return [Food.from_api_data(item, abridged=True) for item in data]