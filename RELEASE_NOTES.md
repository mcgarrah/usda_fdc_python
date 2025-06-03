# Release Notes for v0.1.6

## Overview

Version 0.1.6 is a maintenance release that improves the stability and documentation of the USDA FDC Python Client. This release focuses on fixing the version update script, adding a comprehensive changelog, and improving documentation for examples.

## What's New

### Added
- Added comprehensive CHANGELOG.md file tracking all releases
- Added more detailed examples documentation
- Improved error handling in recipe analysis
- Added RELEASE.md with release process instructions
- Added releasing.rst to the documentation

### Fixed
- Fixed version_update.py script to properly update all version references
- Fixed Python version handling in pyproject.toml
- Updated documentation links and references

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade usda-fdc
```

## Full Changelog

For a complete list of changes, see the [CHANGELOG.md](CHANGELOG.md) file.

## Next Steps

This release finalizes the library for integration with Django web applications. The library now provides a stable API for accessing USDA Food Data Central data, analyzing nutrient content, and integrating with Django applications.