"""
Django views for the USDA FDC library.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from .models import FoodModel, NutrientModel


class FoodListView(ListView):
    """List view for foods."""
    
    model = FoodModel
    paginate_by = 50
    template_name = 'usda_fdc/food_list.html'
    context_object_name = 'foods'
    
    def get_queryset(self):
        """Get the queryset for the view."""
        queryset = super().get_queryset()
        
        # Apply search filter
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(description__icontains=search_query) |
                Q(brand_name__icontains=search_query) |
                Q(ingredients__icontains=search_query)
            )
        
        # Apply data type filter
        data_type = self.request.GET.get('data_type')
        if data_type:
            queryset = queryset.filter(data_type=data_type)
        
        # Apply category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(food_category=category)
        
        # Apply brand filter
        brand = self.request.GET.get('brand')
        if brand:
            queryset = queryset.filter(brand_owner=brand)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        
        # Add search query to context
        context['search_query'] = self.request.GET.get('q', '')
        
        # Add filter values to context
        context['data_type'] = self.request.GET.get('data_type', '')
        context['category'] = self.request.GET.get('category', '')
        context['brand'] = self.request.GET.get('brand', '')
        
        # Add filter options to context
        context['data_types'] = FoodModel.objects.values_list(
            'data_type', flat=True
        ).distinct().order_by('data_type')
        
        context['categories'] = FoodModel.objects.values_list(
            'food_category', flat=True
        ).exclude(food_category__isnull=True).distinct().order_by('food_category')
        
        context['brands'] = FoodModel.objects.values_list(
            'brand_owner', flat=True
        ).exclude(brand_owner__isnull=True).distinct().order_by('brand_owner')
        
        return context


class FoodDetailView(DetailView):
    """Detail view for a food."""
    
    model = FoodModel
    template_name = 'usda_fdc/food_detail.html'
    context_object_name = 'food'
    
    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        
        # Add nutrients to context, grouped by rank
        nutrients = self.object.nutrients.all().order_by('rank', 'name')
        
        # Group nutrients by rank range
        nutrient_groups = {
            'Proximates': [],
            'Minerals': [],
            'Vitamins': [],
            'Lipids': [],
            'Amino Acids': [],
            'Other': []
        }
        
        for nutrient in nutrients:
            rank = nutrient.rank or 0
            
            if rank < 1000:  # Proximates
                nutrient_groups['Proximates'].append(nutrient)
            elif 1000 <= rank < 2000:  # Minerals
                nutrient_groups['Minerals'].append(nutrient)
            elif 2000 <= rank < 3000:  # Vitamins
                nutrient_groups['Vitamins'].append(nutrient)
            elif 3000 <= rank < 4000:  # Lipids
                nutrient_groups['Lipids'].append(nutrient)
            elif 4000 <= rank < 5000:  # Amino Acids
                nutrient_groups['Amino Acids'].append(nutrient)
            else:  # Other
                nutrient_groups['Other'].append(nutrient)
        
        context['nutrient_groups'] = nutrient_groups
        
        # Add portions to context
        context['portions'] = self.object.food_portions.all()
        
        return context


def food_api_view(request, pk):
    """API view for a food."""
    food = get_object_or_404(FoodModel, pk=pk)
    
    # Convert food to JSON
    food_data = {
        'fdc_id': food.fdc_id,
        'description': food.description,
        'data_type': food.data_type,
        'publication_date': food.publication_date.isoformat() if food.publication_date else None,
        'food_class': food.food_class,
        'food_category': food.food_category,
        'brand_owner': food.brand_owner,
        'brand_name': food.brand_name,
        'ingredients': food.ingredients,
        'serving_size': food.serving_size,
        'serving_size_unit': food.serving_size_unit,
        'nutrients': [
            {
                'id': nutrient.nutrient_id,
                'name': nutrient.name,
                'amount': nutrient.amount,
                'unit': nutrient.unit_name
            }
            for nutrient in food.nutrients.all()
        ],
        'portions': [
            {
                'id': portion.portion_id,
                'amount': portion.amount,
                'gram_weight': portion.gram_weight,
                'description': portion.portion_description,
                'measure_unit': portion.measure_unit
            }
            for portion in food.food_portions.all()
        ]
    }
    
    return JsonResponse(food_data)