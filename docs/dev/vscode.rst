VS Code Development
================

This document provides information about using Visual Studio Code for development of the USDA FDC Python Client.

Recommended Extensions
-------------------

The repository includes an ``.vscode/extensions.json`` file that recommends the following extensions:

- **ms-python.python**: Python language support
- **ms-python.vscode-pylance**: Python language server
- **ms-python.black-formatter**: Black code formatter
- **matangover.mypy**: MyPy type checking
- **njpwerner.autodocstring**: Auto-generate docstrings
- **streetsidesoftware.code-spell-checker**: Spell checking
- **ryanluker.vscode-coverage-gutters**: Test coverage visualization
- **ms-toolsai.jupyter**: Jupyter notebook support
- **lextudio.restructuredtext**: reStructuredText support for documentation

You can install these extensions by opening the Extensions view (Ctrl+Shift+X) and searching for "recommended".

Settings
-------

The repository includes VS Code settings in ``.vscode/settings.json`` that configure:

- Python linting with flake8 and mypy
- Code formatting with black
- Automatic import sorting
- Pytest as the testing framework
- Environment variables from .env file

These settings ensure a consistent development experience across the team.

Running Tests
-----------

You can run tests directly from VS Code using the Test Explorer or the provided debug configurations:

1. **Using Test Explorer**:
   - Open the Testing view (flask icon in the sidebar)
   - Click the play button to run all tests
   - Click individual tests to run them separately

2. **Using Debug Configurations**:
   - Open the Run and Debug view (Ctrl+Shift+D)
   - Select a configuration from the dropdown:
     - Python: All Tests
     - Python: Unit Tests
     - Python: Integration Tests
     - Python: Django Tests
   - Click the green play button or press F5

Tasks
-----

The repository includes VS Code tasks in ``.vscode/tasks.json`` that you can run:

1. Open the Command Palette (Ctrl+Shift+P)
2. Select "Tasks: Run Task"
3. Choose from the available tasks:
   - Run All Tests
   - Run Unit Tests
   - Run Integration Tests
   - Run Django Tests
   - Run Tests with Coverage
   - Format Code
   - Sort Imports
   - Lint Code
   - Type Check
   - Build Documentation

Debugging
--------

To debug the code:

1. Set breakpoints by clicking in the gutter next to line numbers
2. Select a debug configuration
3. Start debugging with F5
4. Use the debug toolbar to step through code, inspect variables, etc.

For debugging tests:

1. Open a test file
2. Set breakpoints
3. Use the "Python: Current File" debug configuration

Keyboard Shortcuts
---------------

Useful keyboard shortcuts for Python development in VS Code:

- **F5**: Start debugging
- **Ctrl+Shift+P**: Open Command Palette
- **Ctrl+Space**: Trigger IntelliSense
- **Shift+Alt+F**: Format document
- **F8**: Go to next error or warning
- **F12**: Go to definition
- **Alt+F12**: Peek definition
- **Shift+F12**: Show references
- **Ctrl+.**: Show quick fixes