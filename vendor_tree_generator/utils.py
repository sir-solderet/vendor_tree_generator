import os

def list_proprietary_files(root_dir):
    """
    Recursively find proprietary blobs, example: list all files in /vendor/lib, /vendor/bin, etc.
    Replace with real logic to match your ROMs.
    """
    prop_files = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            abs_path = os.path.join(subdir, file)
            rel_path = os.path.relpath(abs_path, root_dir)
            prop_files.append(rel_path)
    return prop_files
