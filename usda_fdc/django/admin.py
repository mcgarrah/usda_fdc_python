"""
Django admin interface for the USDA FDC models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count

from .models import FoodModel, NutrientModel, FoodPortionModel


class NutrientInline(admin.TabularInline):
    """Inline admin for nutrients."""
    model = NutrientModel
    extra = 0
    fields = ('name', 'amount', 'unit_name', 'rank')
    readonly_fields = ('nutrient_id', 'name', 'unit_name', 'rank')
    can_delete = False
    max_num = 0
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return False


class FoodPortionInline(admin.TabularInline):
    """Inline admin for food portions."""
    model = FoodPortionModel
    extra = 0
    fields = ('amount', 'measure_unit', 'gram_weight', 'portion_description')
    readonly_fields = ('portion_id', 'measure_unit', 'portion_description')
    can_delete = False
    max_num = 0
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(FoodModel)
class FoodAdmin(admin.ModelAdmin):
    """Admin interface for food items."""
    list_display = ('fdc_id', 'description', 'data_type', 'brand_name', 'nutrient_count', 'updated_at')
    list_filter = ('data_type', 'food_category', 'brand_owner', 'updated_at')
    search_fields = ('description', 'brand_name', 'ingredients', 'fdc_id')
    readonly_fields = ('fdc_id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('fdc_id', 'description', 'data_type', 'publication_date')
        }),
        ('Classification', {
            'fields': ('food_class', 'food_category', 'scientific_name')
        }),
        ('Brand Information', {
            'fields': ('brand_owner', 'brand_name')
        }),
        ('Serving Information', {
            'fields': ('serving_size', 'serving_size_unit', 'household_serving_fulltext')
        }),
        ('Content', {
            'fields': ('ingredients',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    inlines = [NutrientInline, FoodPortionInline]
    actions = ['refresh_from_api']
    
    def nutrient_count(self, obj):
        """Return the number of nutrients for this food."""
        return obj.nutrients.count()
    nutrient_count.short_description = 'Nutrients'
    nutrient_count.admin_order_field = 'nutrient_count'
    
    def get_queryset(self, request):
        """Add nutrient count to queryset."""
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(nutrient_count=Count('nutrients'))
        return queryset
    
    def refresh_from_api(self, request, queryset):
        """Refresh selected foods from the API."""
        from ..django.cache import FdcCache
        
        cache = FdcCache()
        fdc_ids = list(queryset.values_list('fdc_id', flat=True))
        cache.refresh(fdc_ids)
        
        self.message_user(request, f"Successfully refreshed {len(fdc_ids)} foods from the API.")
    refresh_from_api.short_description = "Refresh selected foods from the API"


@admin.register(NutrientModel)
class NutrientAdmin(admin.ModelAdmin):
    """Admin interface for nutrients."""
    list_display = ('name', 'amount', 'unit_name', 'food_link')
    list_filter = ('unit_name', 'name')
    search_fields = ('name', 'food__description')
    readonly_fields = ('nutrient_id', 'food', 'name', 'unit_name', 'nutrient_nbr', 'rank')
    
    def food_link(self, obj):
        """Return a link to the food admin page."""
        url = reverse('admin:usda_fdc_django_foodmodel_change', args=[obj.food.fdc_id])
        return format_html('<a href="{}">{}</a>', url, obj.food.description)
    food_link.short_description = 'Food'
    food_link.admin_order_field = 'food__description'
    
    def has_add_permission(self, request):
        """Disable adding nutrients directly."""
        return False


@admin.register(FoodPortionModel)
class FoodPortionAdmin(admin.ModelAdmin):
    """Admin interface for food portions."""
    list_display = ('food_link', 'amount', 'measure_unit', 'gram_weight', 'portion_description')
    list_filter = ('measure_unit',)
    search_fields = ('food__description', 'portion_description')
    readonly_fields = ('portion_id', 'food', 'measure_unit', 'portion_description')
    
    def food_link(self, obj):
        """Return a link to the food admin page."""
        url = reverse('admin:usda_fdc_django_foodmodel_change', args=[obj.food.fdc_id])
        return format_html('<a href="{}">{}</a>', url, obj.food.description)
    food_link.short_description = 'Food'
    food_link.admin_order_field = 'food__description'
    
    def has_add_permission(self, request):
        """Disable adding portions directly."""
        return False