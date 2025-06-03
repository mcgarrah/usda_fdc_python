#!/usr/bin/env python3
"""
Version Update Script for USDA FDC Python Client

This script updates the version number in all necessary files:
- usda_fdc/__init__.py
- pyproject.toml
- setup.py

Usage:
    python version_update.py 0.1.5
"""

import re
import sys
import os


def update_version(new_version):
    """Update version in all required files"""
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print(f"Error: Version '{new_version}' does not match format X.Y.Z")
        return False

    # Update __init__.py
    init_path = os.path.join('usda_fdc', '__init__.py')
    success = update_init_version(init_path, new_version)
    if not success:
        return False

    # Update pyproject.toml - only update the project version, not python_version
    success = update_pyproject_version('pyproject.toml', new_version)
    if not success:
        return False

    # Update setup.py
    success = update_setup_version('setup.py', new_version)
    if not success:
        return False

    print(f"Version updated to {new_version} in all files.")
    return True


def update_init_version(file_path, new_version):
    """Update version in __init__.py file"""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return False

    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()

    # Handle both single and double quotes
    pattern = r'__version__\s*=\s*["\']([^"\']+)["\']'
    match = re.search(pattern, content)
    
    if not match:
        print(f"Error: Could not find __version__ in {file_path}")
        return False
    
    old_version = match.group(1)
    # Preserve the original quote style (single or double)
    quote_char = content[match.start() + content[match.start():].find('=') + 1:].strip()[0]
    
    # Replace the version while preserving the quote style
    updated_content = re.sub(
        pattern, 
        f'__version__ = {quote_char}{new_version}{quote_char}', 
        content
    )

    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(updated_content)

    print(f"Updated {file_path}: {old_version} -> {new_version}")
    return True


def update_pyproject_version(file_path, new_version):
    """Update only the project version in pyproject.toml"""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return False

    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()

    # Find the project section and update the version
    project_section_match = re.search(r'(\[project\][^\[]*?)version\s*=\s*"([^"]+)"', content, re.DOTALL)
    
    if project_section_match:
        before_version = project_section_match.group(1)
        old_version = project_section_match.group(2)
        updated_content = content.replace(
            f'{before_version}version = "{old_version}"', 
            f'{before_version}version = "{new_version}"'
        )
        
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(updated_content)
        
        print(f"Updated {file_path}: {old_version} -> {new_version}")
        return True
    else:
        print(f"Error: Could not find version in [project] section of {file_path}")
        return False


def update_setup_version(file_path, new_version):
    """Update version in setup.py file"""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return False

    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()

    # Match version="X.Y.Z" pattern
    pattern = r'version\s*=\s*"([^"]+)"'
    match = re.search(pattern, content)
    
    if not match:
        print(f"Error: Could not find version in {file_path}")
        return False
    
    old_version = match.group(1)
    updated_content = re.sub(pattern, f'version="{new_version}"', content)

    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(updated_content)

    print(f"Updated {file_path}: {old_version} -> {new_version}")
    return True


def main():
    """Main function"""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} NEW_VERSION")
        print("Example: python version_update.py 0.1.5")
        return 1

    new_version = sys.argv[1]
    success = update_version(new_version)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
