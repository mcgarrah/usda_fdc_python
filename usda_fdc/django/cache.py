"""
Caching layer for Django integration.
"""

import logging
from typing import List, Optional, Union, Dict, Any

from django.conf import settings
from django.core.cache import cache
from django.db import transaction

from ..client import FdcClient
from ..models import Food, SearchResult
from .models import FoodModel, NutrientModel, FoodPortionModel

logger = logging.getLogger(__name__)

class FdcCache:
    """
    Caching layer for the FDC API that stores results in both Django models and cache.
    
    This class provides methods to interact with the FDC API while caching results
    in Django models for persistence and in Django's cache for performance.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        cache_timeout: Optional[int] = None,
        use_cache: bool = True
    ):
        """
        Initialize the FDC cache.
        
        Args:
            api_key: The API key for the FDC API. If not provided, will use settings.FDC_API_KEY.
            cache_timeout: The cache timeout in seconds. If not provided, will use settings.FDC_CACHE_TIMEOUT.
            use_cache: Whether to use the cache. If False, will always fetch from the API.
        """
        self.api_key = api_key or getattr(settings, 'FDC_API_KEY', None)
        self.cache_timeout = cache_timeout or getattr(settings, 'FDC_CACHE_TIMEOUT', 86400)  # Default: 1 day
        self.use_cache = use_cache and getattr(settings, 'FDC_CACHE_ENABLED', True)
        self.client = FdcClient(api_key=self.api_key)
    
    def _get_cache_key(self, prefix: str, *args) -> str:
        """
        Generate a cache key for the given prefix and arguments.
        
        Args:
            prefix: The prefix for the cache key.
            *args: Additional arguments to include in the cache key.
            
        Returns:
            A cache key string.
        """
        return f"fdc:{prefix}:{':'.join(str(arg) for arg in args)}"
    
    def search(
        self, 
        query: str, 
        data_type: Optional[List[str]] = None,
        page_size: int = 50,
        page_number: int = 1,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        brand_owner: Optional[str] = None,
        force_refresh: bool = False
    ) -> SearchResult:
        """
        Search for foods and cache the results.
        
        Args:
            query: The search query.
            data_type: Filter on specific data types.
            page_size: Maximum number of results per page.
            page_number: Page number to retrieve.
            sort_by: Field to sort by.
            sort_order: Sort direction.
            brand_owner: Filter by brand owner.
            force_refresh: Whether to force a refresh from the API.
            
        Returns:
            A SearchResult object.
        """
        cache_key = self._get_cache_key(
            "search", query, data_type, page_size, page_number, sort_by, sort_order, brand_owner
        )
        
        if self.use_cache and not force_refresh:
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit for search: {query}")
                return cached_result
        
        logger.debug(f"Cache miss for search: {query}, fetching from API")
        result = self.client.search(
            query=query,
            data_type=data_type,
            page_size=page_size,
            page_number=page_number,
            sort_by=sort_by,
            sort_order=sort_order,
            brand_owner=brand_owner
        )
        
        if self.use_cache:
            cache.set(cache_key, result, self.cache_timeout)
        
        return result
    
    def get_food(
        self, 
        fdc_id: Union[str, int], 
        format: str = "full", 
        nutrients: Optional[List[int]] = None,
        force_refresh: bool = False
    ) -> Food:
        """
        Get a food by FDC ID and cache the result.
        
        Args:
            fdc_id: The FDC ID of the food.
            format: The format of the response.
            nutrients: List of nutrient IDs to include.
            force_refresh: Whether to force a refresh from the API.
            
        Returns:
            A Food object.
        """
        # Try to get from Django model first
        if self.use_cache and not force_refresh:
            try:
                food_model = FoodModel.objects.get(fdc_id=fdc_id)
                logger.debug(f"Database hit for food: {fdc_id}")
                return food_model.to_food_object()
            except FoodModel.DoesNotExist:
                logger.debug(f"Database miss for food: {fdc_id}")
        
        # If not in database or force refresh, get from API
        logger.debug(f"Fetching food {fdc_id} from API")
        food = self.client.get_food(fdc_id=fdc_id, format=format, nutrients=nutrients)
        
        # Save to database
        if self.use_cache:
            self._save_food_to_database(food)
        
        return food
    
    def get_foods(
        self, 
        fdc_ids: List[Union[str, int]], 
        format: str = "full", 
        nutrients: Optional[List[int]] = None,
        force_refresh: bool = False
    ) -> List[Food]:
        """
        Get multiple foods by FDC ID and cache the results.
        
        Args:
            fdc_ids: List of FDC IDs.
            format: The format of the response.
            nutrients: List of nutrient IDs to include.
            force_refresh: Whether to force a refresh from the API.
            
        Returns:
            A list of Food objects.
        """
        result = []
        missing_ids = []
        
        # Try to get from Django models first
        if self.use_cache and not force_refresh:
            food_models = FoodModel.objects.filter(fdc_id__in=fdc_ids)
            found_ids = {model.fdc_id for model in food_models}
            
            for model in food_models:
                result.append(model.to_food_object())
            
            missing_ids = [fdc_id for fdc_id in fdc_ids if fdc_id not in found_ids]
        else:
            missing_ids = fdc_ids
        
        # If any IDs are missing or force refresh, get from API
        if missing_ids or force_refresh:
            logger.debug(f"Fetching {len(missing_ids)} foods from API")
            api_foods = self.client.get_foods(
                fdc_ids=missing_ids if missing_ids else fdc_ids,
                format=format,
                nutrients=nutrients
            )
            
            # Save to database
            if self.use_cache:
                for food in api_foods:
                    self._save_food_to_database(food)
            
            if force_refresh:
                return api_foods
            else:
                result.extend(api_foods)
        
        return result
    
    def refresh(self, fdc_ids: List[Union[str, int]]) -> None:
        """
        Refresh the cache for specific foods.
        
        Args:
            fdc_ids: List of FDC IDs to refresh.
        """
        self.get_foods(fdc_ids=fdc_ids, force_refresh=True)
    
    @transaction.atomic
    def _save_food_to_database(self, food: Food) -> FoodModel:
        """
        Save a Food object to the database.
        
        Args:
            food: The Food object to save.
            
        Returns:
            The saved FoodModel instance.
        """
        # Create or update the food model
        food_model, created = FoodModel.objects.update_or_create(
            fdc_id=food.fdc_id,
            defaults={
                'description': food.description,
                'data_type': food.data_type,
                'publication_date': food.publication_date,
                'food_class': food.food_class,
                'food_category': food.food_category,
                'scientific_name': food.scientific_name,
                'brand_owner': food.brand_owner,
                'brand_name': food.brand_name,
                'ingredients': food.ingredients,
                'serving_size': food.serving_size,
                'serving_size_unit': food.serving_size_unit,
                'household_serving_fulltext': food.household_serving_fulltext,
            }
        )
        
        # If updating, clear existing nutrients and portions
        if not created:
            NutrientModel.objects.filter(food=food_model).delete()
            FoodPortionModel.objects.filter(food=food_model).delete()
        
        # Create nutrients
        for nutrient in food.nutrients:
            NutrientModel.objects.create(
                food=food_model,
                nutrient_id=nutrient.id,
                name=nutrient.name,
                amount=nutrient.amount,
                unit_name=nutrient.unit_name,
                nutrient_nbr=nutrient.nutrient_nbr,
                rank=nutrient.rank
            )
        
        # Create food portions
        for portion in food.food_portions:
            FoodPortionModel.objects.create(
                food=food_model,
                portion_id=portion.id,
                amount=portion.amount,
                gram_weight=portion.gram_weight,
                portion_description=portion.portion_description,
                modifier=portion.modifier,
                measure_unit=portion.measure_unit
            )
        
        return food_model