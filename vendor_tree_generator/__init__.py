#!/usr/bin/env python3
"""
Vendor Tree Generator
Generate LineageOS/AOSP-style vendor trees from super.img or partition images.
"""

from .extractor import ImageExtractor
from .generator import VendorTreeGenerator
from .utils import setup_logging, check_dependencies

__all__ = [
    "ImageExtractor",
    "VendorTreeGenerator", 
    "setup_logging",
    "check_dependencies"
]
