# --- vendor_tree_generator/extractor.py ---
import os
import subprocess

def run_cmd(cmd):
    print(f"[+] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def unpack_super(super_img_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    run_cmd(["lpunpack", super_img_path, output_dir])

def convert_sparse_img(img_path, raw_img_path):
    run_cmd(["simg2img", img_path, raw_img_path])

def mount_img(raw_img_path, mount_point):
    os.makedirs(mount_point, exist_ok=True)
    run_cmd(["sudo", "mount", "-o", "loop", raw_img_path, mount_point])

def extract_partition(img_path, out_dir, label):
    raw_path = f"{label}_raw.img"
    mnt_path = f"mnt_{label}"
    convert_sparse_img(img_path, raw_path)
    mount_img(raw_path, mnt_path)
    run_cmd(["cp", "-a", f"{mnt_path}/.", out_dir])
    run_cmd(["sudo", "umount", mnt_path])
    os.remove(raw_path)
    os.rmdir(mnt_path)
