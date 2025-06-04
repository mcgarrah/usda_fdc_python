# Changelog

All notable changes to the USDA FDC Python Client will be documented in this file.

## [0.1.7] - 2025-06-04

### Added
- Implemented comprehensive recipe analysis functionality
- Added ingredient parsing and nutritional calculation for recipes
- Created visualization tools for nutrient data with HTML reports
- Added RELEASE.md with release process instructions
- Updated documentation with new features and examples

### Changed
- Renamed command-line tool from fdc-analyze to fdc-nat (Nutrient Analysis Tool)
- Updated package configuration in both setup.py and pyproject.toml

### Fixed
- Fixed version update script to properly handle all version references
- Fixed dotenv loading in client module

## [0.1.6] - 2025-06-03

### Added
- Added comprehensive CHANGELOG.md file
- Added more detailed examples documentation
- Improved error handling in recipe analysis

### Fixed
- Fixed version_update.py script to properly update all version references
- Fixed Python version handling in pyproject.toml
- Updated documentation links and references

## [0.1.5] - 2025-06-03

### Added
- Added 8 comprehensive example scripts demonstrating library functionality
- Created basic examples for searching and retrieving food data
- Added nutrient analysis examples for foods and recipes
- Implemented advanced examples for meal planning and visualization
- Added analyze_version.py example for CLI usage
- Updated documentation with detailed example explanations

### Fixed
- Fixed version_update.py to prevent modifying Python version in pyproject.toml
- Updated README with example information

## [0.1.4] - 2025-06-03

### Added
- Implemented comprehensive nutrient analysis module
- Added dietary reference intake (DRI) data and comparisons
- Created recipe analysis with ingredient parsing
- Added visualization tools for nutrient data
- Implemented command-line interface for nutrient analysis (fdc-analyze)
- Added documentation for nutrient analysis features

## [0.1.3] - 2025-06-03

### Added
- Completed Django integration with admin interface
- Implemented Django admin views for food data
- Added custom filters and search functionality
- Created background tasks for cache warming/refreshing
- Implemented migration scripts for database setup
- Added views and URLs for food data display
- Updated documentation with Django integration details

## [0.1.2] - 2025-06-03

### Added
- Created comprehensive test suite
- Implemented unit tests for all components
- Added integration tests for API interactions
- Created Django-specific tests for models and cache
- Added detailed test fixtures and utilities
- Enhanced documentation with testing instructions
- Added VS Code configuration for development and testing

### Fixed
- Fixed documentation for correct GitHub URL

## [0.1.1] - 2025-06-03

### Added
- Implemented command-line interface (CLI)
- Added comprehensive documentation
- Created user guide and API reference
- Added examples and tutorials
- Implemented error handling and logging

## [0.1.0] - 2025-06-02

### Added
- Initial implementation of USDA FDC Python library
- Created base client class with authentication handling
- Implemented rate limiting and error handling
- Added support for all FDC API endpoints
- Created data models for all FDC data types
- Implemented search functionality with filtering
- Added batch operations for efficient API usage