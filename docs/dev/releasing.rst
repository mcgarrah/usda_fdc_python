Releasing
=========

This document describes the process for releasing new versions of the USDA FDC Python Client.

Version Numbering
---------------

This project follows Semantic Versioning (SemVer):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

Release Process
-------------

1. Update Version
~~~~~~~~~~~~~~~

Update the version number in ``usda_fdc/__init__.py``:

.. code-block:: python

   __version__ = "X.Y.Z"

2. Update Changelog
~~~~~~~~~~~~~~~~

Update the ``CHANGELOG.md`` file with the changes in the new version.

3. Create Release Commit
~~~~~~~~~~~~~~~~~~~~~

Commit the version and changelog changes:

.. code-block:: bash

   git add usda_fdc/__init__.py CHANGELOG.md
   git commit -m "Release vX.Y.Z"

4. Create Git Tag
~~~~~~~~~~~~~~

Create a git tag for the release:

.. code-block:: bash

   git tag -a vX.Y.Z -m "Version X.Y.Z"

5. Push to GitHub
~~~~~~~~~~~~~~

Push the commit and tag to GitHub:

.. code-block:: bash

   git push origin main
   git push origin vX.Y.Z

6. Build Distribution
~~~~~~~~~~~~~~~~~~

Build the distribution packages:

.. code-block:: bash

   python -m build

This will create both a source distribution and a wheel in the ``dist/`` directory.

7. Upload to PyPI
~~~~~~~~~~~~~~

Upload the packages to PyPI:

.. code-block:: bash

   python -m twine upload dist/*

8. Create GitHub Release
~~~~~~~~~~~~~~~~~~~~~

Create a new release on GitHub:

- Go to the repository's releases page
- Click "Draft a new release"
- Select the tag you just created
- Fill in the release title and description
- Attach the distribution files
- Publish the release

9. Update Documentation
~~~~~~~~~~~~~~~~~~~~

Ensure the documentation is updated on Read the Docs:

- Go to the Read the Docs project page
- Trigger a new build if necessary

Post-Release
-----------

After releasing, update the version in ``usda_fdc/__init__.py`` to the next development version:

.. code-block:: python

   __version__ = "X.Y+1.0.dev0"

Commit this change:

.. code-block:: bash

   git add usda_fdc/__init__.py
   git commit -m "Bump version to X.Y+1.0.dev0"
   git push origin main