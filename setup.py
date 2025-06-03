#!/usr/bin/env python3
"""Setup script for the USDA Food Data Central (FDC) Python Client."""

from setuptools import setup, find_packages

# Read the contents of README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="usda-fdc",
    version="0.1.5",
    description="A comprehensive Python library for interacting with the USDA Food Data Central API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Michael McGarrah",
    author_email="mcgarrah@gmail.com",
    url="https://github.com/mcgarrah/usda_fdc_python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pint>=0.17",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "django": ["Django>=3.2"],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "mypy>=0.812",
            "flake8>=3.9.2",
        ],
        "docs": [
            "sphinx>=4.0.2",
            "sphinx-rtd-theme>=0.5.2",
        ],
        "analysis": [
            "matplotlib>=3.4.0",
            "numpy>=1.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fdc=usda_fdc.cli:main",
            "fdc-analyze=usda_fdc.analysis.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "usda_fdc.analysis": ["resources/dri/*.json"],
    },
)