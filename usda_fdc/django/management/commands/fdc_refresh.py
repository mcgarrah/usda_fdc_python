"""
Django management command to refresh the USDA FDC cache.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext_lazy as _

from usda_fdc.django.models import FoodModel
from usda_fdc.django.tasks import refresh_stale_foods, warm_cache


class Command(BaseCommand):
    """
    Refresh the USDA FDC cache.
    
    This command allows refreshing the cache by:
    - Refreshing stale foods that haven't been updated recently
    - Warming the cache with new foods
    """
    
    help = _('Refresh the USDA FDC cache')
    
    def add_arguments(self, parser):
        """Add command arguments."""
        # Mutually exclusive group for refresh method
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--stale',
            action='store_true',
            help=_('Refresh stale foods')
        )
        group.add_argument(
            '--warm',
            action='store_true',
            help=_('Warm the cache with new foods')
        )
        
        # Options for stale foods
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help=_('Number of days since last update (for --stale, default: 30)')
        )
        
        # Options for warm cache
        parser.add_argument(
            '--data-type',
            type=str,
            nargs='+',
            choices=['Branded', 'Foundation', 'Survey', 'SR Legacy'],
            help=_('Data types to include (for --warm)')
        )
        
        # Common options
        parser.add_argument(
            '--limit',
            type=int,
            default=1000,
            help=_('Maximum number of foods to process (default: 1000)')
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=20,
            help=_('Number of foods to process in each batch (default: 20)')
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        if options['stale']:
            self.refresh_stale_foods(options['days'], options['limit'])
        elif options['warm']:
            self.warm_cache(options['data_type'], options['limit'], options['batch_size'])
    
    def refresh_stale_foods(self, days, limit):
        """Refresh foods that haven't been updated recently."""
        self.stdout.write(self.style.NOTICE(
            f"Refreshing foods not updated in the last {days} days (limit: {limit})"
        ))
        
        # Count stale foods
        from django.utils import timezone
        import datetime
        
        cutoff_date = timezone.now() - datetime.timedelta(days=days)
        stale_count = FoodModel.objects.filter(updated_at__lt=cutoff_date).count()
        
        self.stdout.write(self.style.NOTICE(
            f"Found {stale_count} stale foods, refreshing up to {limit}"
        ))
        
        try:
            refresh_stale_foods(days, limit)
            self.stdout.write(self.style.SUCCESS("Successfully refreshed stale foods"))
        except Exception as e:
            raise CommandError(f"Error refreshing stale foods: {e}")
    
    def warm_cache(self, data_type, limit, batch_size):
        """Warm the cache with new foods."""
        data_type_str = ', '.join(data_type) if data_type else 'all'
        self.stdout.write(self.style.NOTICE(
            f"Warming cache with {data_type_str} foods (limit: {limit}, batch size: {batch_size})"
        ))
        
        try:
            warm_cache(data_type, limit, batch_size)
            self.stdout.write(self.style.SUCCESS("Successfully warmed cache"))
        except Exception as e:
            raise CommandError(f"Error warming cache: {e}")