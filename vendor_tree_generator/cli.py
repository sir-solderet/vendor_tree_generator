#!/usr/bin/env python3

import sys
import click
import logging
from colorama import init, Fore, Style

from .extractor import ImageExtractor
from .generator import VendorTreeGenerator
from .utils import setup_logging, check_dependencies

init(autoreset=True)


@click.command()
@click.option(
    "--super", "-s", "super_img",
    type=click.Path(exists=True),
    help="Path to super.img file"
)
@click.option(
    "--partition", "-p", "partition_img",
    type=click.Path(exists=True),
    help="Path to partition image file"
)
@click.option(
    "--output", "-o", "output_dir",
    required=True,
    type=click.Path(),
    help="Output directory for vendor tree"
)
@click.option(
    "--vendor", "-v", "vendor_name",
    required=True,
    help="Vendor name (e.g., samsung)"
)
@click.option(
    "--device", "-d", "device_name",
    required=True,
    help="Device codename (e.g., gta9)"
)
@click.option(
    "--android-version", "-av", "android_version",
    default="13",
    help="Android version (default: 13)"
)
@click.option(
    "--verbose", "-V", is_flag=True,
    help="Enable verbose logging"
)
@click.option(
    "--dry-run", is_flag=True,
    help="Show what would be done without executing"
)
def main(
    super_img,
    partition_img,
    output_dir,
    vendor_name,
    device_name,
    android_version,
    verbose,
    dry_run,
):
    """Generate LineageOS/AOSP-style vendor trees from super.img or partition images."""

    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    if not check_dependencies():
        logger.error(
            "Missing required dependencies. Please install "
            "lpunpack, simg2img, and mount tools."
        )
        sys.exit(1)

    if not super_img and not partition_img:
        logger.error("Either --super or --partition must be specified")
        sys.exit(1)

    if super_img and partition_img:
        logger.error("Cannot specify both --super and --partition")
        sys.exit(1)

    print(f"{Fore.CYAN}{Style.BRIGHT}Vendor Tree Generator v1.0.0{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'=' * 50}{Style.RESET_ALL}")

    try:
        extractor = ImageExtractor(verbose=verbose)

        if super_img:
            logger.info(f"Extracting super.img: {super_img}")
            extracted_path = extractor.extract_super_img(super_img)
        else:
            logger.info(f"Processing partition image: {partition_img}")
            extracted_path = extractor.extract_partition_img(partition_img)

        if not extracted_path:
            logger.error("Failed to extract image")
            sys.exit(1)

        generator = VendorTreeGenerator(
            vendor_name=vendor_name,
            device_name=device_name,
            android_version=android_version,
            verbose=verbose,
        )

        logger.info(f"Generating vendor tree: {output_dir}")

        if not dry_run:
            success = generator.generate_tree(extracted_path, output_dir)
            if success:
                print(
                    f"\n{Fore.GREEN}{Style.BRIGHT}✓ Vendor tree generated successfully!"
                    f"{Style.RESET_ALL}"
                )
                print(f"{Fore.YELLOW}Output: {output_dir}{Style.RESET_ALL}")
            else:
                logger.error("Failed to generate vendor tree")
                sys.exit(1)
        else:
            logger.info("Dry run - no files written")

        extractor.cleanup()

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
