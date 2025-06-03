"""
Django models for the USDA FDC data.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..models import Food, Nutrient, FoodPortion


class FoodModel(models.Model):
    """
    Django model for a food item from the FDC database.
    """
    fdc_id = models.IntegerField(primary_key=True, verbose_name=_("FDC ID"))
    description = models.CharField(max_length=512, verbose_name=_("Description"))
    data_type = models.CharField(max_length=50, verbose_name=_("Data Type"))
    publication_date = models.DateField(null=True, blank=True, verbose_name=_("Publication Date"))
    food_class = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Food Class"))
    food_category = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Food Category"))
    scientific_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Scientific Name"))
    brand_owner = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Brand Owner"))
    brand_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Brand Name"))
    ingredients = models.TextField(null=True, blank=True, verbose_name=_("Ingredients"))
    serving_size = models.FloatField(null=True, blank=True, verbose_name=_("Serving Size"))
    serving_size_unit = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Serving Size Unit"))
    household_serving_fulltext = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Household Serving"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    class Meta:
        verbose_name = _("Food")
        verbose_name_plural = _("Foods")
        indexes = [
            models.Index(fields=["data_type"]),
            models.Index(fields=["brand_owner"]),
            models.Index(fields=["food_category"]),
        ]
    
    def __str__(self):
        return f"{self.description} ({self.fdc_id})"
    
    def to_food_object(self) -> Food:
        """
        Convert the Django model to a Food object.
        
        Returns:
            A Food object.
        """
        nutrients = [nutrient.to_nutrient_object() for nutrient in self.nutrients.all()]
        food_portions = [portion.to_food_portion_object() for portion in self.food_portions.all()]
        
        return Food(
            fdc_id=self.fdc_id,
            description=self.description,
            data_type=self.data_type,
            publication_date=self.publication_date.isoformat() if self.publication_date else None,
            food_class=self.food_class,
            food_category=self.food_category,
            scientific_name=self.scientific_name,
            brand_owner=self.brand_owner,
            brand_name=self.brand_name,
            ingredients=self.ingredients,
            serving_size=self.serving_size,
            serving_size_unit=self.serving_size_unit,
            household_serving_fulltext=self.household_serving_fulltext,
            nutrients=nutrients,
            food_portions=food_portions
        )


class NutrientModel(models.Model):
    """
    Django model for a nutrient in a food item.
    """
    food = models.ForeignKey(FoodModel, on_delete=models.CASCADE, related_name="nutrients", verbose_name=_("Food"))
    nutrient_id = models.IntegerField(verbose_name=_("Nutrient ID"))
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    amount = models.FloatField(verbose_name=_("Amount"))
    unit_name = models.CharField(max_length=50, verbose_name=_("Unit Name"))
    nutrient_nbr = models.IntegerField(null=True, blank=True, verbose_name=_("Nutrient Number"))
    rank = models.IntegerField(null=True, blank=True, verbose_name=_("Rank"))
    
    class Meta:
        verbose_name = _("Nutrient")
        verbose_name_plural = _("Nutrients")
        unique_together = [("food", "nutrient_id")]
        indexes = [
            models.Index(fields=["nutrient_id"]),
            models.Index(fields=["name"]),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.amount} {self.unit_name})"
    
    def to_nutrient_object(self) -> Nutrient:
        """
        Convert the Django model to a Nutrient object.
        
        Returns:
            A Nutrient object.
        """
        return Nutrient(
            id=self.nutrient_id,
            name=self.name,
            amount=self.amount,
            unit_name=self.unit_name,
            nutrient_nbr=self.nutrient_nbr,
            rank=self.rank
        )


class FoodPortionModel(models.Model):
    """
    Django model for a food portion.
    """
    food = models.ForeignKey(FoodModel, on_delete=models.CASCADE, related_name="food_portions", verbose_name=_("Food"))
    portion_id = models.IntegerField(verbose_name=_("Portion ID"))
    amount = models.FloatField(verbose_name=_("Amount"))
    gram_weight = models.FloatField(verbose_name=_("Gram Weight"))
    portion_description = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Portion Description"))
    modifier = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Modifier"))
    measure_unit = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Measure Unit"))
    
    class Meta:
        verbose_name = _("Food Portion")
        verbose_name_plural = _("Food Portions")
        unique_together = [("food", "portion_id")]
    
    def __str__(self):
        return f"{self.amount} {self.measure_unit or ''} ({self.gram_weight}g)"
    
    def to_food_portion_object(self) -> FoodPortion:
        """
        Convert the Django model to a FoodPortion object.
        
        Returns:
            A FoodPortion object.
        """
        return FoodPortion(
            id=self.portion_id,
            amount=self.amount,
            gram_weight=self.gram_weight,
            portion_description=self.portion_description,
            modifier=self.modifier,
            measure_unit=self.measure_unit
        )