#!/usr/bin/env python3

import argparse
from vendor_tree_generator import ImageExtractor, VendorTreeGenerator, setup_logging, check_dependencies

def main():
    parser = argparse.ArgumentParser(description="Vendor Tree Generator")
    parser.add_argument("--vendor", required=True)
    parser.add_argument("--device", required=True)
    parser.add_argument("--images_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--android_version", default="13")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)
    check_dependencies()

    extractor = ImageExtractor(images_dir=args.images_dir)
    extracted_path = extractor.extract()

    generator = VendorTreeGenerator(
        vendor_name=args.vendor,
        device_name=args.device,
        android_version=args.android_version,
        verbose=args.verbose,
    )
    generator.generate_tree(extracted_path=extracted_path, output_dir=args.output_dir)

if __name__ == "__main__":
    main()
