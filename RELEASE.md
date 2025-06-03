# Release Process for USDA FDC Python Client

This document outlines the steps to release a new version of the USDA FDC Python Client.

## Release Checklist

1. **Update Version**
   - Run `python3 version_update.py X.Y.Z` to update version numbers in all files
   - Verify that all version references have been updated correctly

2. **Update Changelog**
   - Ensure CHANGELOG.md is up to date with all notable changes
   - Move items from "Unreleased" to the new version section
   - Add the release date

3. **Run Tests**
   - Run the test suite to ensure everything is working correctly
   - `pytest`
   - `pytest -m integration` (requires API key)
   - `pytest -m django` (requires Django)

4. **Build Documentation**
   - Build and check the documentation
   - `cd docs && make html`
   - Review the generated documentation

5. **Create Release Commit**
   - Commit the version changes with a message like "Release vX.Y.Z"
   - `git add .`
   - `git commit -m "Release vX.Y.Z"`

6. **Create Git Tag**
   - Create a tag for the new version
   - `git tag -a vX.Y.Z -m "Version X.Y.Z"`

7. **Push to GitHub**
   - Push the commit and tag to GitHub
   - `git push origin main`
   - `git push origin vX.Y.Z`

8. **Build and Upload to PyPI**
   - Build the distribution packages
   - `python -m build`
   - Upload to PyPI
   - `python -m twine upload dist/*`

9. **Verify Installation**
   - Verify the package can be installed from PyPI
   - `pip install --no-cache-dir --upgrade usda-fdc`

10. **Update Documentation**
    - Trigger a documentation build on ReadTheDocs
    - Verify the new documentation is available

## Post-Release

1. **Announce the Release**
   - Update the GitHub release notes
   - Notify users if appropriate

2. **Start Next Development Cycle**
   - Update version to next development version (X.Y.Z-dev)
   - `python3 version_update.py X.Y.Z-dev`