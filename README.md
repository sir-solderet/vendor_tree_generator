# Vendor Tree Generator

Generate LineageOS/AOSP-style vendor trees from `super.img` or partition images with ease.
 
# GTA9 Extracted Images

These files were extracted from the `super.img` partition of the Samsung GTA9 device.

| Partition        | Purpose                    |
|------------------|-----------------------------|
| `vendor.img`     | Vendor-specific binaries    |
| `system.img`     | Android OS system files     |
| `product.img`    | Product-specific overlays   |
| `odm.img`        | ODM-specific configuration  |
| `system_ext.img` | Extensions to the system    |
| `vendor_dlkm.img`| Kernel modules for vendor   |

- Generate vendor tree files including:  
  - `proprietary-files.txt` (lists proprietary blobs)  
  - `Android.mk` (legacy makefile)  
  - `Android.bp` (soong build file)  
  - `BoardConfig.mk` and device vendor makefiles  
- Supports Android 8.0+ (Oreo/API 26) and above  
- Designed to simplify custom ROM device setup  

## Requirements

- Python 3.8 or higher  
- Linux system with `lpunpack`, `simg2img`, `mount`, and `sudo` installed  

Install required tools (Ubuntu/Debian example):  
- sudo apt-get update
- sudo apt-get install lpunpack simg2img mount sudo

## Installation

Clone the repository and install dependencies:
- git clone https://github.com/sir-solderet/vendor_tree_generator.git
- cd vendor_tree_generator
- pip3 install -r requirements.txt

## Usage

### Generate vendor tree from `super.img`
python3 -m vendor_tree_generator.cli --partition path/to/vendor.img --output vendor_yourvendor_yourdevice --vendor yourvendor --device yourdevice --android-version 15

### Options

- `--super` / `-s`: Path to the `super.img` file  
- `--partition` / `-p`: Path to a single partition image (e.g., `vendor.img`)  
- `--output` / `-o`: Output directory for the generated vendor tree  
- `--vendor` / `-v`: Vendor name (e.g., `samsung`)  
- `--device` / `-d`: Device codename (e.g., `gta9`)  
- `--android-version` / `-av`: Android version (default is `15`)  
- `--verbose` / `-V`: Enable verbose output for debugging

## Example

See the `examples/run_example.sh` script for a sample usage workflow.

## Contributing

Contributions and suggestions are welcome! Please open issues or pull requests.
