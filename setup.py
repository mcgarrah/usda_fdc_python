#!/usr/bin/env python3
"""
Setup script for the USDA FDC Python Client.
"""

from setuptools import setup, find_packages

setup(
    name="usda_fdc",
    version="0.1.8",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.25.0",
        "pint>=0.17",
        "python-dotenv>=0.19.0"
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
        "docs": ["sphinx>=4.0.2", "sphinx-rtd-theme>=0.5.2"],
    },
    entry_points={
        "console_scripts": [
            "fdc=usda_fdc.cli:main",
            "fdc-nat=usda_fdc.analysis.cli:main",
        ],
    },
    package_data={
        "usda_fdc": ["analysis/resources/dri/*.json"],
    },
)