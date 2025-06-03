"""
Initial migration for USDA FDC models.
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Initial migration for USDA FDC models."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='FoodModel',
            fields=[
                ('fdc_id', models.IntegerField(primary_key=True, serialize=False, verbose_name='FDC ID')),
                ('description', models.CharField(max_length=512, verbose_name='Description')),
                ('data_type', models.CharField(max_length=50, verbose_name='Data Type')),
                ('publication_date', models.DateField(blank=True, null=True, verbose_name='Publication Date')),
                ('food_class', models.CharField(blank=True, max_length=50, null=True, verbose_name='Food Class')),
                ('food_category', models.CharField(blank=True, max_length=255, null=True, verbose_name='Food Category')),
                ('scientific_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Scientific Name')),
                ('brand_owner', models.CharField(blank=True, max_length=255, null=True, verbose_name='Brand Owner')),
                ('brand_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Brand Name')),
                ('ingredients', models.TextField(blank=True, null=True, verbose_name='Ingredients')),
                ('serving_size', models.FloatField(blank=True, null=True, verbose_name='Serving Size')),
                ('serving_size_unit', models.CharField(blank=True, max_length=50, null=True, verbose_name='Serving Size Unit')),
                ('household_serving_fulltext', models.CharField(blank=True, max_length=255, null=True, verbose_name='Household Serving')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
            ],
            options={
                'verbose_name': 'Food',
                'verbose_name_plural': 'Foods',
                'indexes': [
                    models.Index(fields=['data_type'], name='fdc_data_type_idx'),
                    models.Index(fields=['brand_owner'], name='fdc_brand_owner_idx'),
                    models.Index(fields=['food_category'], name='fdc_food_category_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='NutrientModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nutrient_id', models.IntegerField(verbose_name='Nutrient ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('amount', models.FloatField(verbose_name='Amount')),
                ('unit_name', models.CharField(max_length=50, verbose_name='Unit Name')),
                ('nutrient_nbr', models.IntegerField(blank=True, null=True, verbose_name='Nutrient Number')),
                ('rank', models.IntegerField(blank=True, null=True, verbose_name='Rank')),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nutrients', to='usda_fdc_django.foodmodel', verbose_name='Food')),
            ],
            options={
                'verbose_name': 'Nutrient',
                'verbose_name_plural': 'Nutrients',
                'unique_together': {('food', 'nutrient_id')},
                'indexes': [
                    models.Index(fields=['nutrient_id'], name='fdc_nutrient_id_idx'),
                    models.Index(fields=['name'], name='fdc_nutrient_name_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='FoodPortionModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('portion_id', models.IntegerField(verbose_name='Portion ID')),
                ('amount', models.FloatField(verbose_name='Amount')),
                ('gram_weight', models.FloatField(verbose_name='Gram Weight')),
                ('portion_description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Portion Description')),
                ('modifier', models.CharField(blank=True, max_length=255, null=True, verbose_name='Modifier')),
                ('measure_unit', models.CharField(blank=True, max_length=50, null=True, verbose_name='Measure Unit')),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='food_portions', to='usda_fdc_django.foodmodel', verbose_name='Food')),
            ],
            options={
                'verbose_name': 'Food Portion',
                'verbose_name_plural': 'Food Portions',
                'unique_together': {('food', 'portion_id')},
            },
        ),
    ]