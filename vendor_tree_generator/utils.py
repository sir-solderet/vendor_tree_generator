import os

def extract_files(image_path, output_dir):
    """
    Stub: Simulate extracting files from a partition image.
    In production, use lpunpack/simg2img/mount with subprocess.
    """
    proprietary_dir = os.path.join(output_dir, "proprietary")
    os.makedirs(proprietary_dir, exist_ok=True)
    dummy_files = ["libdummy.so", "vendor_dummy.bin"]

    # Create dummy proprietary files
    for fname in dummy_files:
        with open(os.path.join(proprietary_dir, fname), "w") as f:
            f.write("This is a placeholder for " + fname)
    
    # Return the list of proprietary files relative to output_dir
    return [os.path.join("proprietary", fname) for fname in dummy_files]


def generate_prop_files(proprietary_files, output_dir):
    """
    Generate proprietary-files.txt listing all blobs.
    """
    prop_path = os.path.join(output_dir, "proprietary-files.txt")
    with open(prop_path, "w") as f:
        for path in proprietary_files:
            f.write(path + "\n")


def generate_android_mk(output_dir, proprietary_files):
    """
    Generate a basic Android.mk for vendor blobs.
    """
    mk_path = os.path.join(output_dir, "Android.mk")
    vendor_name = os.path.basename(output_dir)

    mk_content = f"""# Auto-generated Android.mk for {vendor_name}
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE := proprietary-blobs
LOCAL_SRC_FILES := {' '.join(proprietary_files)}
include $(BUILD_PREBUILT)
"""
    with open(mk_path, "w") as f:
        f.write(mk_content)
