import argparse
import logging
import sys
from pathlib import Path

from vendor_tree_generator.generator import VendorTreeGenerator


def run_cli():
    parser = argparse.ArgumentParser(
        description="Generate a vendor tree from extracted Android partition images."
    )
    parser.add_argument("--vendor", required=True, help="Vendor name (e.g., samsung)")
    parser.add_argument("--device", required=True, help="Device codename (e.g., gta9)")
    parser.add_argument(
        "--images", required=True, help="Path to directory containing partition images"
    )
    parser.add_argument(
        "--output", default="vendor_output", help="Path to output vendor tree"
    )
    parser.add_argument(
        "--android-version", default="13", help="Android version (default: 13)"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose debug output"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(levelname)s] %(message)s",
    )

    image_dir = Path(args.images)
    partitions = [
        "vendor.img",
        "system.img",
        "product.img",
        "odm.img",
        "system_ext.img",
        "vendor_dlkm.img",
    ]
    image_paths = [image_dir / img for img in partitions if (image_dir / img).exists()]

    if not image_paths:
        logging.error("No valid *.img files found in the provided images directory.")
        sys.exit(1)

    generator = VendorTreeGenerator(
        vendor_name=args.vendor,
        device_name=args.device,
        android_version=args.android_version,
        verbose=args.verbose,
    )

    for image_path in image_paths:
        generator.extract_image(image_path)

    success = generator.generate_tree("extracted", args.output)
    if success:
        logging.info("Vendor tree generated at: %s", args.output)
    else:
        logging.error("Failed to generate vendor tree.")
        sys.exit(1)
