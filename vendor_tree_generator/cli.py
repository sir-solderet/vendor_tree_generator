#!/usr/bin/env python3

import argparse
import logging
import os

from .generator import VendorTreeGenerator
from .utils import setup_logging


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate AOSP/LineageOS-style vendor tree from partition images"
    )
    parser.add_argument(
        "--vendor", required=True, help="Vendor name (e.g., samsung)"
    )
    parser.add_argument(
        "--device", required=True, help="Device codename (e.g., gta9)"
    )
    parser.add_argument(
        "--image-dir", required=True, help="Path to directory with extracted .img files"
    )
    parser.add_argument(
        "--output-dir", default="vendor_tree", help="Output directory (default: vendor_tree)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    return parser.parse_args()


def run():
    args = parse_args()
    setup_logging(args.verbose)

    device_output_path = os.path.join(args.output_dir, args.device)

    generator = VendorTreeGenerator(
        vendor_name=args.vendor,
        device_name=args.device,
        verbose=args.verbose,
    )

    success = generator.generate_tree(args.image_dir, device_output_path)

    if success:
        logging.info("Vendor tree generated at: %s", device_output_path)
    else:
        logging.error("Failed to generate vendor tree.")
