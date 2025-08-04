import os
from .utils import list_proprietary_files

def generate_vendor_tree(partitions_path, output_dir):
    """
    Copy out vendor blobs, create proprietary-files.txt and Android.mk.
    """
    # Copy proprietary files to output/
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # List all proprietary files (stub example)
    prop_files = list_proprietary_files(partitions_path)

    # Write proprietary-files.txt
    with open(os.path.join(output_dir, "proprietary-files.txt"), "w") as f:
        for path in prop_files:
            f.write(f"{path}\n")

    # Write Android.mk
    with open(os.path.join(output_dir, "Android.mk"), "w") as f:
        f.write("LOCAL_PATH := $(call my-dir)\n")
        f.write("# ... rest of your Android.mk specifics ...\n")
