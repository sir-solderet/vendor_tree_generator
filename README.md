# vendor-tree-generator

A tool to generate AOSP or LineageOS-style vendor trees from super.img or split images (system.img, vendor.img, etc.).

## Features

- Extracts proprietary blobs from super.img or device
- Auto-generates `proprietary-files.txt`
- Builds full vendor tree structure
- Supports multiple partition layouts

## Usage

```bash
python3 -m vendor_tree_generator.cli --super super.img --output vendor_samsung_gta9
