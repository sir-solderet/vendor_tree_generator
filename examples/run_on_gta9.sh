#!/bin/bash

# Example usage of vendor tree generator

# Set variables
SUPER_IMG="/path/to/super.img"
VENDOR_NAME="samsung"
DEVICE_NAME="gta9"
OUTPUT_DIR="vendor_${VENDOR_NAME}_${DEVICE_NAME}"

# Run the generator
python3 -m vendor_tree_generator.cli \
    --super "$SUPER_IMG" \
    --output "$OUTPUT_DIR" \
    --vendor "$VENDOR_NAME" \
    --device "$DEVICE_NAME" \
    --android-version "13" \
    --verbose

echo "Vendor tree generated in: $OUTPUT_DIR"
echo "Next steps:"
echo "1. Review the generated proprietary-files.txt"
echo "2. Test the Android.mk and Android.bp files"
echo "3. Adjust any paths or dependencies as needed"
echo "4. Commit the vendor tree to your ROM project"
