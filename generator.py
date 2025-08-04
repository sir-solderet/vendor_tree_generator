# --- vendor_tree_generator/generator.py ---
import os

def generate_proprietary_files_txt(vendor_path, out_path):
    with open(out_path, 'w') as f:
        for root, dirs, files in os.walk(vendor_path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, vendor_path)
                f.write(f"{rel_path}\n")

def create_android_mk(vendor_dir):
    mk_path = os.path.join(vendor_dir, "Android.mk")
    with open(mk_path, 'w') as f:
        f.write("# Auto-generated Android.mk\n")
        f.write("include $(CLEAR_VARS)\n")
        f.write("LOCAL_MODULE := proprietary-blobs\n")
        f.write("include $(BUILD_PREBUILT)\n")
