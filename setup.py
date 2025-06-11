#!/usr/bin/env python3
"""
Setup script per 5bands_labeler
Labeler per immagini multispettrali con 5 bande
"""

from setuptools import setup, find_packages
from pathlib import Path

# Leggi README per descrizione lunga
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Leggi requirements
requirements = []
with open('requirements.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            requirements.append(line)

setup(
    name="5bands_labeler",
    version="1.0.0",
    author="HPL Project",
    author_email="hpl@example.com",
    description="Labeler per immagini multispettrali con 5 bande (MicaSense Red Edge)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hpl/5bands_labeler",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Image Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "5bands-labeler=gui.labeling_gui:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
