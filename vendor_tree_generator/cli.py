import argparse
from pathlib import Path
from .main import generate_vendor_tree
from .utils import download_images_if_needed

def main():
    parser = argparse.ArgumentParser(description="Vendor Tree Generator CLI")
    parser.add_argument("--vendor", required=True, help="Vendor name (e.g., samsung)")
    parser.add_argument("--device", required=True, help="Device codename (e.g., gta9)")
    parser.add_argument("--images-dir", default="images/gta9", help="Path to extracted .img files")
    parser.add_argument("--output", default="output", help="Output directory for vendor tree")

    args = parser.parse_args()

    image_dir = Path(args.images_dir)
    download_images_if_needed(image_dir, args.device)

    generate_vendor_tree(
        vendor_name=args.vendor,
        device_name=args.device,
        images_dir=image_dir,
        output_dir=args.output
    )

if __name__ == "__main__":
    main()
