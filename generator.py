#!/usr/bin/env python3

import os
import shutil
import logging
import subprocess
from pathlib import Path


class VendorTreeGenerator:
    def __init__(self, vendor_name, device_name, android_version="13", verbose=False):
        self.vendor = vendor_name
        self.device = device_name
        self.android_version = android_version
        self.verbose = verbose
        self.extract_dir = Path("extracted")
        self.proprietary_files = []

    def extract_image(self, image_path: Path):
        name = image_path.stem
        out_dir = self.extract_dir / name
        out_dir.mkdir(parents=True, exist_ok=True)

        simg2img_path = shutil.which("simg2img") or "/usr/bin/simg2img"
        debugfs_path = shutil.which("debugfs") or "/usr/bin/debugfs"
        use_raw_img = out_dir / f"{name}.raw.img"

        logging.info(f"Extracting image: {image_path.name}")
        try:
            subprocess.run([simg2img_path, str(image_path), str(use_raw_img)], check=True)
            subprocess.run(["sudo", debugfs_path, "-R", f"rdump / {out_dir}", str(use_raw_img)], check=True)
            logging.info(f"Extracted {name} using simg2img and debugfs")
        except Exception as e:
            logging.warning(f"simg2img or debugfs failed for {image_path.name}: {e}")
            try:
                subprocess.run(["7z", "x", str(image_path), f"-o{out_dir}"], check=True)
                logging.info(f"Extracted to {out_dir}")
            except subprocess.CalledProcessError as e:
                logging.error(f"[7z] Failed to extract {image_path.name}: {e}")

        logging.debug(f"Extracted contents to: {out_dir}")

    def scan_proprietary_files(self):
        for partition in self.extract_dir.iterdir():
            for root, _, files in os.walk(partition):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), partition)
                    if self.is_proprietary_file(rel_path):
                        self.proprietary_files.append((partition.name, rel_path))
                        logging.debug(f"Found proprietary file: {partition.name}/{rel_path}")

    def is_proprietary_file(self, rel_path):
        skip_paths = ["META-INF", "resources.arsc", "AndroidManifest.xml", "NOTICE.html.gz"]
        return not any(part in rel_path for part in skip_paths)

    def copy_proprietary_files(self, output_dir: Path):
        for partition, rel_path in self.proprietary_files:
            src = self.extract_dir / partition / rel_path
            dst = output_dir / "proprietary" / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    def write_android_mk(self, output_dir: Path):
        mk_path = output_dir / "Android.mk"
        mk_path.write_text(f"""
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE := {self.device}-vendor
LOCAL_MODULE_CLASS := ETC
LOCAL_SRC_FILES := proprietary-files.txt
include $(BUILD_PREBUILT)
""".strip())

    def write_android_bp(self, output_dir: Path):
        bp_path = output_dir / "Android.bp"
        bp_path.write_text(f"""
prebuilt_etc {{
    name: "{self.device}-vendor",
    src: "proprietary-files.txt",
    sub_dir: "vendor/{self.vendor}/{self.device}",
    installable: false,
}}
""".strip())

    def write_boardconfig(self, output_dir: Path):
        path = output_dir / "BoardConfig.mk"
        path.write_text(f"# BoardConfig for {self.vendor}/{self.device}")

    def write_device_mk(self, output_dir: Path):
        path = output_dir / f"{self.device}-vendor.mk"
        content = f"""
# Auto-generated vendor makefile

PRODUCT_COPY_FILES += \\
"""
        for _, rel_path in self.proprietary_files:
            line = f"    vendor/{self.vendor}/{self.device}/proprietary/{rel_path}:{rel_path} \\\n"
            content += line

        path.write_text(content.strip())

    def write_proprietary_files_txt(self, output_dir: Path):
        path = output_dir / "proprietary-files.txt"
        with path.open("w") as f:
            for _, rel_path in self.proprietary_files:
                f.write(rel_path + "\n")

    def generate_tree(self, extracted_path: str, output_path: str):
        self.extract_dir = Path(extracted_path)
        output_dir = Path(output_path)

        logging.info(f"Created directory structure in {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

        logging.info("Scanning for proprietary files...")
        self.scan_proprietary_files()
        logging.info(f"Found {len(self.proprietary_files)} proprietary files")

        logging.info("Copying proprietary files...")
        self.copy_proprietary_files(output_dir)

        self.write_android_mk(output_dir)
        logging.info("Generated Android.mk")

        self.write_android_bp(output_dir)
        logging.info("Generated Android.bp")

        self.write_boardconfig(output_dir)
        logging.info("Generated BoardConfig.mk")

        self.write_device_mk(output_dir)
        logging.info(f"Generated {self.device}-vendor.mk")

        self.write_proprietary_files_txt(output_dir)
        logging.info(f"Generated proprietary-files.txt with {len(self.proprietary_files)} files")

        logging.info(f"Generated vendor tree with {len(self.proprietary_files)} proprietary files")
        return True
