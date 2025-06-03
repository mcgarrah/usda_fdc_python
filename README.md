# USDA Food Data Central (FDC) Python Client

A comprehensive Python library for interacting with the USDA Food Data Central API, designed for easy integration with Django applications and local database caching.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- Complete API coverage for the USDA Food Data Central (FDC) database
- Object-oriented interface for working with food data
- Comprehensive data models for all FDC data types
- Efficient caching mechanisms for Django integration
- Support for searching, filtering, and retrieving detailed nutritional information
- Conversion utilities for different measurement units
- Batch operations for efficient API usage
- Command-line interface for quick data access
- Nutrient analysis with dietary reference intake comparisons
- Recipe analysis with ingredient parsing and nutritional calculations
- Visualization tools for nutrient data
- Detailed documentation and examples

## Installation

```bash
pip install usda-fdc
```

Or install from source:

```bash
git clone https://github.com/mcgarrah/usda_fdc_python.git
cd usda_fdc
pip install -e .
```

## Quick Start

```python
from usda_fdc import FdcClient

# Initialize the client with your API key
client = FdcClient("YOUR_API_KEY")

# Search for foods
results = client.search("apple")
for food in results.foods:
    print(f"{food.description} (FDC ID: {food.fdc_id})")

# Get detailed information for a specific food
food = client.get_food(1750340)
print(f"Food: {food.description}")
print(f"Data Type: {food.data_type}")

# Get nutrients for a food
nutrients = client.get_nutrients(1750340)
for nutrient in nutrients:
    print(f"{nutrient.name}: {nutrient.amount} {nutrient.unit_name}")
```

## Command-Line Interface

The library includes a command-line interface for quick access to FDC data:

```bash
# Set your API key (or use --api-key parameter)
export FDC_API_KEY=your_api_key_here

# Search for foods
fdc search "apple"

# Get detailed information for a specific food
fdc food 1750340

# Get nutrients for a food
fdc nutrients 1750340

# List foods with pagination
fdc list --page-size 5 --page-number 1

# Get help
fdc --help
```

## Nutrient Analysis

The library includes tools for analyzing nutrient content:

```python
from usda_fdc import FdcClient
from usda_fdc.analysis import analyze_food, DriType, Gender

# Initialize the client
client = FdcClient("YOUR_API_KEY")

# Get a food
food = client.get_food(1750340)  # Apple, raw, with skin

# Analyze the food
analysis = analyze_food(
    food,
    dri_type=DriType.RDA,
    gender=Gender.MALE,
    serving_size=100.0
)

# Access the analysis results
print(f"Calories: {analysis.calories_per_serving} kcal")
print(f"Protein: {analysis.get_nutrient('protein').amount} g")
print(f"Vitamin C: {analysis.get_nutrient('vitamin_c').amount} mg")
```

## Recipe Analysis

The library also supports recipe analysis:

```python
from usda_fdc import FdcClient
from usda_fdc.analysis.recipe import create_recipe, analyze_recipe

# Initialize the client
client = FdcClient("YOUR_API_KEY")

# Create a recipe
recipe = create_recipe(
    name="Fruit Salad",
    ingredient_texts=[
        "1 apple",
        "1 banana",
        "100g strawberries"
    ],
    client=client,
    servings=2
)

# Analyze the recipe
analysis = analyze_recipe(recipe)

# Access the analysis results
per_serving = analysis.per_serving_analysis
print(f"Calories per serving: {per_serving.calories_per_serving} kcal")
```

## Django Integration

The library is designed to work seamlessly with Django applications:

```python
from usda_fdc.django import FdcCache

# Initialize the cache with your Django models
cache = FdcCache()

# Search and cache results
results = cache.search("banana")

# Get food from cache or API
food = cache.get_food(1750340)

# Refresh cache for specific foods
cache.refresh([1750340, 1750341])
```

## Testing

The library includes a comprehensive test suite:

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all unit tests
pytest

# Run integration tests (requires API key)
pytest -m integration

# Run Django tests (requires Django)
pytest -m django

# Run tests with coverage
pytest --cov=usda_fdc
```

## Documentation

For detailed documentation, visit [docs.example.com/usda_fdc](https://docs.example.com/usda_fdc).

## Configuration

Create a `.env` file in your project root with the following variables:

```
FDC_API_KEY=your_api_key_here
FDC_API_URL=https://api.nal.usda.gov/fdc/v1
FDC_CACHE_ENABLED=True
FDC_CACHE_TIMEOUT=86400
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run the tests to ensure they pass (`pytest`)
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- USDA Food Data Central for providing the API and data
- Inspired by various Python USDA FDC clients