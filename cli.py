# --- vendor_tree_generator/cli.py ---
import argparse
import os
from .extractor import unpack_super, extract_partition
from .generator import generate_proprietary_files_txt, create_android_mk

def main():
    parser = argparse.ArgumentParser(description="Vendor Tree Generator")
    parser.add_argument("--super", help="Path to super.img")
    parser.add_argument("--output", help="Output vendor directory")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    print("[*] Unpacking super.img...")
    unpack_dir = os.path.join(args.output, "unpacked")
    unpack_super(args.super, unpack_dir)

    # Look for vendor.img inside unpacked/
    for name in ["vendor", "system", "product", "odm"]:
        img_path = os.path.join(unpack_dir, f"{name}.img")
        if os.path.exists(img_path):
            print(f"[*] Extracting {name}.img")
            extract_partition(img_path, args.output, name)

    print("[*] Generating proprietary-files.txt...")
    generate_proprietary_files_txt(args.output, os.path.join(args.output, "proprietary-files.txt"))
    
    print("[*] Creating Android.mk...")
    create_android_mk(args.output)

if __name__ == '__main__':
    main()
