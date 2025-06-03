"""
URL patterns for the USDA FDC Django integration.
"""

from django.urls import path

from . import views

app_name = 'usda_fdc'

urlpatterns = [
    path('foods/', views.FoodListView.as_view(), name='food_list'),
    path('foods/<int:pk>/', views.FoodDetailView.as_view(), name='food_detail'),
    path('api/foods/<int:pk>/', views.food_api_view, name='food_api'),
]