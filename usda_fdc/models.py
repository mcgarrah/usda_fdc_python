"""
Data models for the USDA FDC API.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime


@dataclass
class Nutrient:
    """
    Represents a nutrient in a food item.
    """
    id: int
    name: str
    amount: float
    unit_name: str
    nutrient_nbr: Optional[int] = None
    rank: Optional[int] = None
    
    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> 'Nutrient':
        """
        Create a Nutrient instance from API data.
        
        Args:
            data: The API response data for a nutrient.
            
        Returns:
            A Nutrient instance.
        """
        nutrient_data = data.get('nutrient', {})
        return cls(
            id=nutrient_data.get('id'),
            name=nutrient_data.get('name'),
            amount=data.get('amount', 0),
            unit_name=nutrient_data.get('unitName'),
            nutrient_nbr=nutrient_data.get('number'),
            rank=nutrient_data.get('rank')
        )


@dataclass
class FoodPortion:
    """
    Represents a food portion.
    """
    id: int
    amount: float
    gram_weight: float
    portion_description: Optional[str] = None
    modifier: Optional[str] = None
    measure_unit: Optional[str] = None
    
    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> 'FoodPortion':
        """
        Create a FoodPortion instance from API data.
        
        Args:
            data: The API response data for a food portion.
            
        Returns:
            A FoodPortion instance.
        """
        measure_unit_data = data.get('measureUnit', {})
        return cls(
            id=data.get('id'),
            amount=data.get('amount', 0),
            gram_weight=data.get('gramWeight', 0),
            portion_description=data.get('portionDescription'),
            modifier=data.get('modifier'),
            measure_unit=measure_unit_data.get('name')
        )


@dataclass
class Food:
    """
    Represents a food item from the FDC database.
    """
    fdc_id: int
    description: str
    data_type: str
    publication_date: Optional[str] = None
    food_class: Optional[str] = None
    food_category: Optional[str] = None
    scientific_name: Optional[str] = None
    brand_owner: Optional[str] = None
    brand_name: Optional[str] = None
    ingredients: Optional[str] = None
    serving_size: Optional[float] = None
    serving_size_unit: Optional[str] = None
    household_serving_fulltext: Optional[str] = None
    nutrients: List[Nutrient] = field(default_factory=list)
    food_portions: List[FoodPortion] = field(default_factory=list)
    
    @classmethod
    def from_api_data(cls, data: Dict[str, Any], abridged: bool = False) -> 'Food':
        """
        Create a Food instance from API data.
        
        Args:
            data: The API response data for a food.
            abridged: Whether the data is in abridged format.
            
        Returns:
            A Food instance.
        """
        food = cls(
            fdc_id=data.get('fdcId'),
            description=data.get('description', ''),
            data_type=data.get('dataType', ''),
            publication_date=data.get('publicationDate'),
            food_class=data.get('foodClass'),
            food_category=data.get('foodCategory', {}).get('description') if data.get('foodCategory') else None,
            scientific_name=data.get('scientificName'),
            brand_owner=data.get('brandOwner'),
            brand_name=data.get('brandName'),
            ingredients=data.get('ingredients'),
            serving_size=data.get('servingSize'),
            serving_size_unit=data.get('servingSizeUnit'),
            household_serving_fulltext=data.get('householdServingFullText')
        )
        
        # Parse nutrients if present
        if 'foodNutrients' in data and not abridged:
            food.nutrients = [
                Nutrient.from_api_data(nutrient) 
                for nutrient in data['foodNutrients'] 
                if 'nutrient' in nutrient
            ]
        
        # Parse food portions if present
        if 'foodPortions' in data and not abridged:
            food.food_portions = [
                FoodPortion.from_api_data(portion) 
                for portion in data['foodPortions']
            ]
        
        return food


@dataclass
class SearchResultFood:
    """
    Represents a food item in search results.
    """
    fdc_id: int
    description: str
    data_type: str
    publication_date: Optional[str] = None
    food_category: Optional[str] = None
    brand_owner: Optional[str] = None
    brand_name: Optional[str] = None
    
    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> 'SearchResultFood':
        """
        Create a SearchResultFood instance from API data.
        
        Args:
            data: The API response data for a search result food.
            
        Returns:
            A SearchResultFood instance.
        """
        return cls(
            fdc_id=data.get('fdcId'),
            description=data.get('description', ''),
            data_type=data.get('dataType', ''),
            publication_date=data.get('publicationDate'),
            food_category=data.get('foodCategory'),
            brand_owner=data.get('brandOwner'),
            brand_name=data.get('brandName')
        )


@dataclass
class SearchResult:
    """
    Represents search results from the FDC API.
    """
    foods: List[SearchResultFood]
    total_hits: int
    current_page: int
    total_pages: int
    
    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> 'SearchResult':
        """
        Create a SearchResult instance from API data.
        
        Args:
            data: The API response data for search results.
            
        Returns:
            A SearchResult instance.
        """
        foods = [
            SearchResultFood.from_api_data(food) 
            for food in data.get('foods', [])
        ]
        
        return cls(
            foods=foods,
            total_hits=data.get('totalHits', 0),
            current_page=data.get('currentPage', 1),
            total_pages=data.get('totalPages', 1)
        )