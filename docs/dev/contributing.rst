Contributing
============

Thank you for considering contributing to the USDA FDC Python Client! This document provides guidelines and instructions for contributing to the project.

Setting Up Development Environment
--------------------------------

1. Fork the repository on GitHub.

2. Clone your fork locally:

   .. code-block:: bash

      git clone https://github.com/yourusername/usda_fdc.git
      cd usda_fdc

3. Install development dependencies:

   .. code-block:: bash

      pip install -e ".[dev]"

4. Set up pre-commit hooks:

   .. code-block:: bash

      pre-commit install

Code Style
---------

This project uses:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

You can run these tools manually:

.. code-block:: bash

   # Format code
   black usda_fdc tests
   
   # Sort imports
   isort usda_fdc tests
   
   # Lint code
   flake8 usda_fdc tests
   
   # Type check
   mypy usda_fdc

Or use pre-commit to run them automatically:

.. code-block:: bash

   pre-commit run --all-files

Testing
------

Please write tests for new features and bug fixes. This project uses pytest:

.. code-block:: bash

   # Run all tests
   pytest
   
   # Run tests with coverage
   pytest --cov=usda_fdc

See :doc:`testing` for more details.

Documentation
------------

Please update documentation for any changes:

1. Update docstrings for any modified functions or classes.
2. Update or add RST files in the ``docs/`` directory as needed.
3. Build and check the documentation locally:

   .. code-block:: bash

      cd docs
      make html
      # Open _build/html/index.html in your browser

Pull Request Process
------------------

1. Create a new branch for your feature or bugfix:

   .. code-block:: bash

      git checkout -b feature-or-bugfix-name

2. Make your changes and commit them with clear, descriptive commit messages.

3. Push your branch to your fork:

   .. code-block:: bash

      git push origin feature-or-bugfix-name

4. Submit a pull request to the main repository.

5. Ensure the CI checks pass.

6. Address any feedback from maintainers.

Code of Conduct
-------------

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.