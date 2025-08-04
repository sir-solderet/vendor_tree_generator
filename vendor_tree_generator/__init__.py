# vendor_tree_generator/__init__.py

from .utils import extract_files, generate_android_mk, generate_prop_files

def generate_vendor_tree(image_path, output_dir):
    # 1. Extract proprietary files from image
    proprietary_files = extract_files(image_path, output_dir)

    # 2. Generate proprietary-files.txt
    generate_prop_files(proprietary_files, output_dir)

    # 3. Generate Android.mk
    generate_android_mk(output_dir, proprietary_files)
