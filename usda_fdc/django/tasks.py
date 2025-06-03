"""
Background tasks for the USDA FDC Django integration.

This module provides background tasks for cache warming and refreshing.
It's designed to work with Celery, Django Q, or other task queues.
"""

import logging
from typing import List, Union, Optional

from .cache import FdcCache
from .models import FoodModel

logger = logging.getLogger(__name__)


def refresh_food(fdc_id: Union[str, int]) -> None:
    """
    Refresh a single food from the API.
    
    Args:
        fdc_id: The FDC ID of the food to refresh.
    """
    cache = FdcCache()
    try:
        cache.get_food(fdc_id, force_refresh=True)
        logger.info(f"Successfully refreshed food {fdc_id}")
    except Exception as e:
        logger.error(f"Error refreshing food {fdc_id}: {e}")


def refresh_foods(fdc_ids: List[Union[str, int]]) -> None:
    """
    Refresh multiple foods from the API.
    
    Args:
        fdc_ids: List of FDC IDs to refresh.
    """
    cache = FdcCache()
    try:
        cache.refresh(fdc_ids)
        logger.info(f"Successfully refreshed {len(fdc_ids)} foods")
    except Exception as e:
        logger.error(f"Error refreshing foods: {e}")


def warm_cache(
    data_type: Optional[List[str]] = None,
    limit: int = 1000,
    batch_size: int = 20
) -> None:
    """
    Warm the cache by fetching foods from the API.
    
    Args:
        data_type: Filter by data type (e.g., ["Branded", "Foundation"]).
        limit: Maximum number of foods to fetch.
        batch_size: Number of foods to fetch in each batch.
    """
    cache = FdcCache()
    client = cache.client
    
    # Get foods from the API
    try:
        # First, get the list of foods
        foods = []
        page = 1
        while len(foods) < limit:
            page_foods = client.list_foods(
                data_type=data_type,
                page_size=min(200, limit - len(foods)),
                page_number=page
            )
            
            if not page_foods:
                break
                
            foods.extend(page_foods)
            page += 1
            
            if len(page_foods) < 200:
                break
        
        logger.info(f"Found {len(foods)} foods to cache")
        
        # Then, fetch the details in batches
        for i in range(0, len(foods), batch_size):
            batch = foods[i:i+batch_size]
            fdc_ids = [food.fdc_id for food in batch]
            
            try:
                cache.get_foods(fdc_ids, force_refresh=True)
                logger.info(f"Cached batch {i//batch_size + 1}/{(len(foods) + batch_size - 1)//batch_size}")
            except Exception as e:
                logger.error(f"Error caching batch {i//batch_size + 1}: {e}")
                
    except Exception as e:
        logger.error(f"Error warming cache: {e}")


def refresh_stale_foods(days: int = 30, limit: int = 1000) -> None:
    """
    Refresh foods that haven't been updated in a specified number of days.
    
    Args:
        days: Number of days since last update.
        limit: Maximum number of foods to refresh.
    """
    from django.utils import timezone
    import datetime
    
    cache = FdcCache()
    cutoff_date = timezone.now() - datetime.timedelta(days=days)
    
    stale_foods = FoodModel.objects.filter(
        updated_at__lt=cutoff_date
    ).order_by('updated_at')[:limit]
    
    fdc_ids = list(stale_foods.values_list('fdc_id', flat=True))
    
    if fdc_ids:
        logger.info(f"Refreshing {len(fdc_ids)} stale foods")
        try:
            cache.refresh(fdc_ids)
            logger.info(f"Successfully refreshed {len(fdc_ids)} stale foods")
        except Exception as e:
            logger.error(f"Error refreshing stale foods: {e}")
    else:
        logger.info("No stale foods found")


# Example usage with Celery:
"""
from celery import shared_task

@shared_task
def refresh_food_task(fdc_id):
    refresh_food(fdc_id)

@shared_task
def refresh_foods_task(fdc_ids):
    refresh_foods(fdc_ids)

@shared_task
def warm_cache_task(data_type=None, limit=1000, batch_size=20):
    warm_cache(data_type, limit, batch_size)

@shared_task
def refresh_stale_foods_task(days=30, limit=1000):
    refresh_stale_foods(days, limit)
"""

# Example usage with Django Q:
"""
from django_q.tasks import async_task

def schedule_refresh_food(fdc_id):
    async_task(refresh_food, fdc_id)

def schedule_refresh_foods(fdc_ids):
    async_task(refresh_foods, fdc_ids)

def schedule_warm_cache(data_type=None, limit=1000, batch_size=20):
    async_task(warm_cache, data_type, limit, batch_size)

def schedule_refresh_stale_foods(days=30, limit=1000):
    async_task(refresh_stale_foods, days, limit)
"""