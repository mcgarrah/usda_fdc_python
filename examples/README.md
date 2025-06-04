# USDA FDC Python Client Examples

This directory contains example scripts demonstrating how to use the USDA FDC Python Client library.

## Setup

Before running these examples, make sure you have:

1. Installed the library: `pip install usda-fdc` or `pip install -e .` from the repository root
2. Set your FDC API key as an environment variable: `export FDC_API_KEY=your_api_key_here`

Alternatively, you can create a `.env` file in this directory with the following content:

```
FDC_API_KEY=your_api_key_here
```

## Basic Examples

### 1. Basic Search (`01_basic_search.py`)

Demonstrates how to search for foods using the USDA FDC API.

```bash
python 01_basic_search.py
```

### 2. Food Details (`02_food_details.py`)

Shows how to retrieve detailed information about specific foods.

```bash
python 02_food_details.py
```

## Nutrient Analysis Examples

### 3. Nutrient Analysis (`03_nutrient_analysis.py`)

Demonstrates how to analyze the nutrient content of a food and compare to dietary reference intakes.

```bash
python 03_nutrient_analysis.py
```

### 4. Compare Foods (`04_compare_foods.py`)

Shows how to compare the nutrient content of multiple foods.

```bash
python 04_compare_foods.py
```

### 5. Recipe Analysis (`05_recipe_analysis.py`)

Demonstrates how to create and analyze recipes.

```bash
python 05_recipe_analysis.py
```

## Advanced Examples

### 6. Django Integration (`06_django_integration.py`)

Shows how to use the library with Django for caching API responses.

```bash
python 06_django_integration.py
```

### 7. Advanced Analysis (`07_advanced_analysis.py`)

Demonstrates advanced nutrient analysis features, including meal planning and visualization.

```bash
python 07_advanced_analysis.py
```

### 8. Command-Line Interface (`08_analyze_version.py`)

Shows how to use the nutrient analysis command-line interface.

```bash
python 08_analyze_version.py
```

### 9. Meal Planning (`09_meal_planning.py`)

Demonstrates how to create and analyze a meal plan with multiple recipes and calculate daily nutritional totals.

```bash
python 09_meal_planning.py
```

### 10. Visualization (`10_visualization.py`)

Shows how to create interactive visualizations of nutrient data, including charts and HTML reports.

```bash
python 10_visualization.py
```

## Notes

- These examples require an API key from the USDA Food Data Central API.
- You can get an API key by registering at https://fdc.nal.usda.gov/api-key-signup.html
- Some examples generate output files in the current directory.
- The Django integration example requires Django to be installed.
- The visualization example requires a web browser to view the generated charts.