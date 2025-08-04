#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vendor_tree_generator",
    description="Generate LineageOS/AOSP-style vendor trees from super.img or partition images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vendor_tree_generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "colorama>=0.4.4",
        "tqdm>=4.62.0",
    ],
    entry_points={
        "console_scripts": [
            "vendor-tree-gen=vendor_tree_generator.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "vendor_tree_generator": ["../config/*.json"],
    },
)
