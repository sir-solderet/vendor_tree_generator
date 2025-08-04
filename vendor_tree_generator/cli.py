import argparse
import sys
from .extractor import extract_partitions
from .generator import generate_vendor_tree

def main():
    parser = argparse.ArgumentParser(description="Vendor Tree Generator")
    parser.add_argument('--super', type=str, help="Path to super.img or partition images", required=True)
    parser.add_argument('--output', type=str, help="Output directory for vendor tree", required=True)
    parser.add_argument('--temp', type=str, help="Optional: temp working dir", default='/tmp/vendor_tree_gen')
    args = parser.parse_args()

    print(f"Extracting partitions from {args.super} ...")
    partitions_path = extract_partitions(args.super, args.temp)  # Returns path where system/vendor/product are extracted

    print(f"Generating vendor tree at {args.output} ...")
    generate_vendor_tree(partitions_path, args.output)

    print("Vendor tree generation complete.")

if __name__ == "__main__":
    main()
