import argparse
import os
from . import generate_vendor_tree

def main():
    parser = argparse.ArgumentParser(description='Vendor Tree Generator (Skeleton)')
    parser.add_argument('--super', dest='image', required=True,
                        help='Path to super.img or partition image')
    parser.add_argument('--output', dest='output', required=True,
                        help='Output vendor tree directory')
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    generate_vendor_tree(args.image, args.output)
    print(f"Vendor tree generated at {args.output}")

if __name__ == "__main__":
    main()
