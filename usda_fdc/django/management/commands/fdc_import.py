"""
Django management command to import data from the USDA FDC API.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext_lazy as _

from usda_fdc.django.cache import FdcCache


class Command(BaseCommand):
    """
    Import data from the USDA FDC API.
    
    This command allows importing food data from the USDA FDC API
    by FDC ID, search query, or data type.
    """
    
    help = _('Import data from the USDA FDC API')
    
    def add_arguments(self, parser):
        """Add command arguments."""
        # Mutually exclusive group for import method
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--fdc-id',
            type=str,
            help=_('Import a specific food by FDC ID')
        )
        group.add_argument(
            '--search',
            type=str,
            help=_('Import foods matching a search query')
        )
        group.add_argument(
            '--data-type',
            type=str,
            nargs='+',
            choices=['Branded', 'Foundation', 'Survey', 'SR Legacy'],
            help=_('Import foods of specific data types')
        )
        
        # Optional arguments
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help=_('Maximum number of foods to import (default: 100)')
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help=_('Force refresh of existing foods')
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        cache = FdcCache()
        
        if options['fdc_id']:
            self.import_by_fdc_id(cache, options['fdc_id'], options['force'])
        elif options['search']:
            self.import_by_search(cache, options['search'], options['limit'], options['force'])
        elif options['data_type']:
            self.import_by_data_type(cache, options['data_type'], options['limit'], options['force'])
    
    def import_by_fdc_id(self, cache, fdc_id, force):
        """Import a food by FDC ID."""
        self.stdout.write(self.style.NOTICE(f"Importing food with FDC ID: {fdc_id}"))
        
        try:
            food = cache.get_food(fdc_id, force_refresh=force)
            self.stdout.write(self.style.SUCCESS(f"Successfully imported: {food.description}"))
        except Exception as e:
            raise CommandError(f"Error importing food with FDC ID {fdc_id}: {e}")
    
    def import_by_search(self, cache, query, limit, force):
        """Import foods matching a search query."""
        self.stdout.write(self.style.NOTICE(f"Searching for foods matching: {query}"))
        
        try:
            # First, search for foods
            results = cache.search(query, page_size=min(limit, 200))
            
            if not results.foods:
                self.stdout.write(self.style.WARNING(f"No foods found matching: {query}"))
                return
            
            self.stdout.write(self.style.NOTICE(
                f"Found {results.total_hits} foods, importing up to {limit}"
            ))
            
            # Then import each food
            count = 0
            for food_result in results.foods[:limit]:
                try:
                    food = cache.get_food(food_result.fdc_id, force_refresh=force)
                    self.stdout.write(
                        self.style.SUCCESS(f"Imported: {food.description} ({food.fdc_id})")
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error importing {food_result.fdc_id}: {e}")
                    )
            
            self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} foods"))
            
        except Exception as e:
            raise CommandError(f"Error searching for foods: {e}")
    
    def import_by_data_type(self, cache, data_types, limit, force):
        """Import foods of specific data types."""
        self.stdout.write(self.style.NOTICE(f"Importing foods of types: {', '.join(data_types)}"))
        
        try:
            # Get foods from the API
            client = cache.client
            
            # First, get the list of foods
            foods = []
            page = 1
            while len(foods) < limit:
                page_foods = client.list_foods(
                    data_type=data_types,
                    page_size=min(200, limit - len(foods)),
                    page_number=page
                )
                
                if not page_foods:
                    break
                    
                foods.extend(page_foods)
                page += 1
                
                if len(page_foods) < 200:
                    break
            
            self.stdout.write(self.style.NOTICE(f"Found {len(foods)} foods, importing..."))
            
            # Then import each food
            count = 0
            for i, food_summary in enumerate(foods):
                try:
                    food = cache.get_food(food_summary.fdc_id, force_refresh=force)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"[{i+1}/{len(foods)}] Imported: {food.description} ({food.fdc_id})"
                        )
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"[{i+1}/{len(foods)}] Error importing {food_summary.fdc_id}: {e}"
                        )
                    )
            
            self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} foods"))
            
        except Exception as e:
            raise CommandError(f"Error importing foods: {e}")