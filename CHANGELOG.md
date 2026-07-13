# Changelog

All notable changes to the USDA FDC Python Client will be documented in this file.

## [0.2.0] - 2026-07-13

The minor version is bumped because behaviour changes: code that caught every
failure as one exception, or that formatted `dri_percent` without a `None` check,
may need a small edit. See [the migration guide](docs/user/migration.rst).

Every one of these is the same defect wearing a different hat. The old code did
not fail — it *answered*, with a plausible number that was wrong or an exception
that said nothing. A food's kilojoules were served as its calories, an upper
limit was 1000x out, a missing food was indistinguishable from a broken API. For
nutrition data, quietly wrong is worse than loudly absent, so 0.2.0 prefers
`None` and a specific error over a confident fabrication.

### Breaking changes
- **HTTP 404, 403 and 400 now raise `FdcResourceNotFoundError`, `FdcAuthError`
  and `FdcValidationError`** instead of a bare `FdcApiError`. All still derive
  from `FdcApiError`, so a broad `except FdcApiError` is unaffected; only code
  branching on the exception's exact type sees a difference.
- **`dri_percent` is now `None` when the food's unit cannot be compared to the
  DRI's** (vitamin A in IU against a µg allowance), where it previously produced
  a wrong number. Guard for `None` before formatting it.
- **`get_dri(..., DriType.UL)` returns a value where it used to return `None`** —
  expressed in grams, since that is the unit `ul.json` uses. Direct callers who
  assumed milligrams must check the unit; `get_dri_value` now returns it
  alongside the number. `analyze_food` handles the conversion itself.
- **`calories_per_serving` may differ from what an earlier version reported** for
  foods listing energy in both kcal and kJ — because it was previously wrong. See
  0.1.11. Stored calorie figures for affected foods are worth recomputing.

### Added
- `status_code` on `FdcApiError` and every exception deriving from it, holding
  the HTTP status the API replied with (`None` when the request never reached
  the API, as with a refused connection or a timeout). The documentation has
  told callers to branch on this attribute for some time, including a
  retry-on-5xx example that could never have run: nothing ever set it, so
  `hasattr(e, 'status_code')` was always `False`.
- `get_dri_value`, which returns a DRI together with its unit.
- `FdcValidationError` and `FdcResourceNotFoundError` are now exported from the
  package root, alongside the exceptions that were already there.

### Fixed
- **An invalid API key raised a nondescript `FdcApiError`.** FDC sits behind
  api.data.gov, which rejects a bad key with HTTP **403**, while only 401 was
  being mapped — so the single most common mistake a caller can make missed
  `FdcAuthError` entirely. Both statuses now raise it.
- **A missing food and a rejected request were indistinguishable from a broken
  API.** HTTP 404 now raises `FdcResourceNotFoundError` and HTTP 400 raises
  `FdcValidationError`. Both classes had been defined, documented, and never
  raised by anything.
- **Only `DriType.RDA` ever returned data.** `ul.json` ships real Tolerable
  Upper Intake Levels, but under a different schema than `get_dri` knew how to
  read, so every UL lookup came back `None`. Both schemas are now understood.
  `DriType.AI`, `EAR` and `AMDR` ship no data at all; they still return `None`,
  but now log a warning saying so once, rather than leaving an empty DRI column
  unexplained.
- **DRI percentages ignored units.** The shipped data does not use one scale
  throughout: iron's RDA is `8` mg, its UL is `0.045` **g**. `analyze_food`
  divided a food's amount by the DRI as a bare number, so a serving of spinach
  measured against iron's upper limit would have reported **2802%** of it
  instead of 2.8%. Amounts are now converted into the DRI's unit first, and a
  pair that cannot be compared at all — vitamin A in IU against a µg allowance —
  yields no percentage rather than a confident wrong one.

## [0.1.11] - 2026-07-13

### Security
- The API key is now sent as an `X-Api-Key` header instead of an `api_key` query
  parameter, and is redacted from error messages. `requests` embeds the full URL
  in its exception text, so a key in the query string was written into the
  caller's tracebacks, log files and error tracker the first time the network
  hiccuped:

  ```
  FdcApiError: Request failed: ... Max retries exceeded with url:
  /fdc/v1/food/1750340?format=full&api_key=YOUR_REAL_KEY
  ```

  No API change: `FdcClient(api_key=...)` and `FDC_API_KEY` work as before.

### Fixed
- **A food's kilojoules could be reported as its calories.** FDC lists energy
  several times per food under the same name — `1008` (kcal), `1062` (the same
  energy in kJ), and the Atwater variants `2047`/`2048` (kcal). All of them were
  matched on the name alone and keyed as `calories`, so whichever came last in
  the list won. Clarified butter (`fdc_id` 171314) lists 900 kcal and then
  3766 kJ, and `analyze_food` reported **3766 calories** — which the CLI and the
  HTML report then printed with a `kcal` suffix.

  Energy is now matched on its nutrient id/number and unit: only kcal rows can
  become `calories`, the plain `Energy` row is preferred over the Atwater
  variants so the result never depends on list order, and the kJ figure is kept
  under `energy_kj` rather than discarded.

- **`format="abridged"` silently returned a food with no nutrients.** An
  abridged response inlines each nutrient's fields on the row and carries no
  nutrient id, while `format="full"` nests them under a `nutrient` key. Only the
  nested shape was parsed, and the rest were dropped without a word: ghee came
  back with 0 nutrients instead of 18. Both shapes are now understood, so
  anyone reaching for abridged to save bandwidth no longer computes nutrition
  from an empty list.

## [0.1.10] - 2026-07-13

### Added
- `gtin_upc` on `Food` and `SearchResultFood`, parsed from the API's `gtinUpc`
  field. Branded foods carry a barcode and the API has always returned it, but
  both models dropped it.

  This matters because FDC exposes no barcode-lookup endpoint: looking a
  product up by barcode means using the full-text search, which returns fuzzy
  matches — an unknown barcode happily comes back with an unrelated product.
  Without `gtin_upc` a caller has no way to verify a hit is the barcode it
  asked for, and ends up attributing one product's nutrition to another
  product's barcode. Consumers previously had to read the raw search payload
  to work around this.

- `timeout` on `FdcClient` (default 30s, `usda_fdc.client.DEFAULT_TIMEOUT`),
  applied to every request.

- `FdcTimeoutError`, raised when a request exceeds the timeout. It subclasses
  `FdcApiError`, so existing `except FdcApiError` handlers keep working, but
  callers can now tell "slow" from "broken" — a timeout is usually worth
  retrying, a 400 is not.

### Fixed
- **Requests could block forever.** `requests` has no default timeout and none
  was passed, so a server that accepted the connection and then never answered
  hung the calling thread indefinitely — not for a while, forever.

  This punished async consumers hardest: they run this synchronous client in a
  thread pool, and their own `asyncio.wait_for` frees the caller but cannot
  cancel the blocking call underneath, so the thread was lost for the life of
  the process. Enough stalled calls and the pool was dead.

## [0.1.9] - 2025-06-06

### Added
- Added comprehensive examples documentation in docs/user/examples.rst
- Added meal planning example (09_meal_planning.py) for creating and analyzing meal plans
- Added visualization example (10_visualization.py) for creating interactive charts
- Added breakfast_dri_chart.json sample data for visualization examples
- Added examples/data directory for sample data files

### Changed
- Renamed example scripts for better organization:
  - 06_meal_planning.py → 09_meal_planning.py
  - 07_visualization.py → 10_visualization.py
- Updated examples/README.md with descriptions of all example scripts

### Fixed
- Fixed attribute reference in nutrient analysis example (display_name → name)
- Improved error handling in visualization module

## [0.1.8] - 2025-06-05

### Fixed
- Fixed example script errors in nutrient analysis examples
- Fixed DRI chart visualization to properly scale percentage values
- Corrected attribute reference from display_name to name in Nutrient class usage
- Improved error handling in visualization module

### Added
- Added breakfast_dri_chart.json for sample visualization data

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