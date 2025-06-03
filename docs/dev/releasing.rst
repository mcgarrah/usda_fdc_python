Releasing
=========

This document outlines the process for releasing a new version of the USDA FDC Python Client.

Release Process
-------------

1. Update Version
^^^^^^^^^^^^^^^

Run the version update script to update all version references:

.. code-block:: bash

   python3 version_update.py X.Y.Z

This will update the version in:

- ``usda_fdc/__init__.py``
- ``pyproject.toml``
- ``setup.py``

2. Update Changelog
^^^^^^^^^^^^^^^^

Ensure the ``CHANGELOG.md`` file is up to date with all notable changes:

- Move items from "Unreleased" to the new version section
- Add the release date
- Group changes by type (Added, Changed, Fixed, etc.)

3. Run Tests
^^^^^^^^^^

Run the test suite to ensure everything is working correctly:

.. code-block:: bash

   # Run unit tests
   pytest
   
   # Run integration tests (requires API key)
   pytest -m integration
   
   # Run Django tests (requires Django)
   pytest -m django
   
   # Run with coverage
   pytest --cov=usda_fdc

4. Build Documentation
^^^^^^^^^^^^^^^^^^^

Build and check the documentation:

.. code-block:: bash

   cd docs
   make html
   # Open _build/html/index.html in your browser

5. Create Release Commit
^^^^^^^^^^^^^^^^^^^^^

Commit the version changes:

.. code-block:: bash

   git add .
   git commit -m "Release vX.Y.Z"

6. Create Git Tag
^^^^^^^^^^^^^^

Create a tag for the new version:

.. code-block:: bash

   git tag -a vX.Y.Z -m "Version X.Y.Z"

7. Push to GitHub
^^^^^^^^^^^^^^

Push the commit and tag to GitHub:

.. code-block:: bash

   git push origin main
   git push origin vX.Y.Z

8. Build and Upload to PyPI
^^^^^^^^^^^^^^^^^^^^^^^^

Build the distribution packages:

.. code-block:: bash

   python -m build

Upload to PyPI:

.. code-block:: bash

   python -m twine upload dist/*

9. Verify Installation
^^^^^^^^^^^^^^^^^^^

Verify the package can be installed from PyPI:

.. code-block:: bash

   pip install --no-cache-dir --upgrade usda-fdc

10. Update Documentation
^^^^^^^^^^^^^^^^^^^^^

Trigger a documentation build on ReadTheDocs and verify the new documentation is available.

Post-Release
-----------

1. Announce the Release
^^^^^^^^^^^^^^^^^^^^

Update the GitHub release notes with the changelog content.

2. Start Next Development Cycle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Update version to next development version:

.. code-block:: bash

   python3 version_update.py X.Y.(Z+1)-dev