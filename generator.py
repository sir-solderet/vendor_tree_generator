#!/usr/bin/env python3

import logging
import os
import shutil
import subprocess
from pathlib import Path

class VendorTreeGenerator:
    def __init__(self, vendor_name, device_name, android_version="13", verbose=False):
        self.vendor_name = vendor_name.lower()
        self.device_name = device_name.lower()
        self.android_version = android_version
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        self.extracted_dir = Path("extracted")
        self.extracted_dir.mkdir(exist_ok=True)

    def extract_image(self, image_path: Path):
        extract_dir = self.extracted_dir / image_path.stem
        extract_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("Extracting image: %s", image_path.name)

        raw_image = extract_dir / "raw.img"
        try:
            subprocess.run(
                ["simg2img", str(image_path), str(raw_image)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.logger.debug("[simg2img] Converted to raw: %s", raw_image)

            # Extract using debugfs
            dump_cmd = f"rdump / {extract_dir}\nquit\n"
            subprocess.run(
                ["debugfs", str(raw_image)],
                input=dump_cmd.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.logger.info("Extracted to %s", extract_dir)

        except subprocess.CalledProcessError as e:
            self.logger.warning(
                "simg2img or debugfs failed for %s: %s", image_path.name, e.stderr.decode()
            )
            try:
                subprocess.run(
                    ["7z", "x", str(image_path), f"-o{extract_dir}"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.logger.info("[7z] Extracted to %s", extract_dir)
            except subprocess.CalledProcessError as se:
                self.logger.error("[7z] Failed to extract %s: %s", image_path.name, se.stderr.decode())

        if not any(extract_dir.iterdir()):
            self.logger.warning("No files extracted from %s", image_path.name)

    def scan_proprietary_files(self):
        proprietary_files = []
        for partition_dir in self.extracted_dir.iterdir():
            for root, _, files in os.walk(partition_dir):
                for file in files:
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(partition_dir)
                    if self._is_proprietary(file_path):
                        entry = f"{partition_dir.name}/{rel_path}".replace(" ", "\\ ")
                        proprietary_files.append(entry)
                        self.logger.debug("Found proprietary file: %s", entry)
        return sorted(proprietary_files)

    def _is_proprietary(self, file_path: Path):
        # Placeholder: mark everything except common text/docs as proprietary
        return file_path.suffix not in [".txt", ".xml", ".html", ".gz", ".md", ".pb"]

    def generate_tree(self, extracted_dir, output_dir):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        self.logger.info("Created directory structure in %s", output_path)

        proprietary_files = self.scan_proprietary_files()
        self.logger.info("Found %d proprietary files", len(proprietary_files))

        # Copy files into proprietary folder (if needed later)
        # for file in proprietary_files:
        #     src = self.extracted_dir / file
        #     dest = output_path / "proprietary" / file
        #     dest.parent.mkdir(parents=True, exist_ok=True)
        #     shutil.copy2(src, dest)

        self._write_android_mk(output_path)
        self._write_android_bp(output_path)
        self._write_boardconfig(output_path)
        self._write_vendor_mk(output_path)
        self._write_proprietary_files(output_path, proprietary_files)

        self.logger.info("Generated vendor tree with %d proprietary files", len(proprietary_files))
        return True

    def _write_android_mk(self, out_dir: Path):
        mk_path = out_dir / "Android.mk"
        mk_path.write_text(f"""\
LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
LOCAL_MODULE := vendor_{self.device_name}_blob
LOCAL_MODULE_CLASS := ETC
LOCAL_MODULE_PATH := $(TARGET_OUT_VENDOR)/etc
LOCAL_SRC_FILES := proprietary-files.txt
include $(BUILD_PREBUILT)
""")

        self.logger.info("Generated Android.mk")

    def _write_android_bp(self, out_dir: Path):
        bp_path = out_dir / "Android.bp"
        bp_path.write_text(f"""\
package {{
    default_visibility: ["//visibility:public"],
}}

prebuilt_etc {{
    name: "vendor_{self.device_name}_blob",
    src: "proprietary-files.txt",
    sub_dir: "etc",
    installable: true,
}}
""")
        self.logger.info("Generated Android.bp")

    def _write_boardconfig(self, out_dir: Path):
        config_path = out_dir / "BoardConfig.mk"
        config_path.write_text(f"""\
# BoardConfig.mk for {self.device_name}
TARGET_VENDOR := {self.vendor_name}
TARGET_DEVICE := {self.device_name}
""")
        self.logger.info("Generated BoardConfig.mk")

    def _write_vendor_mk(self, out_dir: Path):
        mk_name = f"{self.device_name}-vendor.mk"
        mk_path = out_dir / mk_name
        mk_path.write_text(f"""\
# {mk_name}
PRODUCT_COPY_FILES += \\
    $(call find-copy-subdir-files,*,{self.device_name}/proprietary,system/vendor)
""")
        self.logger.info("Generated %s", mk_name)

    def _write_proprietary_files(self, out_dir: Path, files: list):
        txt_path = out_dir / "proprietary-files.txt"
        with txt_path.open("w") as f:
            for file in files:
                f.write(f"{file}\n")
        self.logger.info("Generated proprietary-files.txt with %d files", len(files))
