# USDA Food Data Central (FDC) Python Client

A comprehensive Python library for interacting with the USDA Food Data Central API, designed for easy integration with Django applications and local database caching.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- Complete API coverage for the USDA FoodData Central (FDC) database
- Object-oriented interface for working with food data
- Comprehensive data models for all FDC data types
- Efficient caching mechanisms for Django integration
- Support for searching, filtering, and retrieving detailed nutritional information
- Conversion utilities for different measurement units
- Batch operations for efficient API usage
- Detailed documentation and examples

## Installation

```bash
pip install usda-fdc
```

Or install from source:

```bash
git clone https://github.com/yourusername/usda_fdc.git
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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- USDA Food Data Central for providing the API and data
- Inspired by various Python USDA FDC clients