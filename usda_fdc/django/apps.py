"""
Django app configuration for the USDA FDC library.
"""

from django.apps import AppConfig


class UsdaFdcConfig(AppConfig):
    """Django app configuration for the USDA FDC library."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usda_fdc.django'
    verbose_name = 'USDA Food Data Central'
    
    def ready(self):
        """
        Initialize the app when Django is ready.
        
        This method is called when the Django app registry is fully populated.
        """
        # Import signals or perform other initialization here
        pass