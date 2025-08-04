#!/usr/bin/env python3

import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict

from templates import VendorTreeTemplates
from utils import get_file_info, is_elf_file


class VendorTreeGenerator:
    """Generates vendor tree structure and files."""

    def __init__(self, vendor_name, device_name, android_version="13", verbose=False):
        self.vendor_name = vendor_name
        self.device_name = device_name
        self.android_version = android_version
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        self.templates = VendorTreeTemplates(vendor_name, device_name, android_version)
        self.proprietary_patterns = self._load_proprietary_patterns()
        self.proprietary_files = []

    def extract_image(self, image_path: Path):
        """Extracts an Android partition image using 7z and fallback."""
        extract_dir = Path("extracted") / image_path.stem
        extract_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("Extracting image: %s", image_path.name)

        raw_image = image_path
        if image_path.suffix == ".br":
            self.logger.error("Brotli compression not yet supported.")
            return

        try:
            subprocess.run(
                ["7z", "x", str(raw_image), f"-o{extract_dir}"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError:
            self.logger.warning("7z extraction failed. Attempting lpmake fallback...")
            # TODO: Implement lpunpack fallback if needed

        self.logger.info("Extracted to %s", extract_dir)

    def generate_tree(self, extracted_path: str, output_dir: str) -> bool:
        try:
            self._create_directory_structure(output_dir)
            self._scan_proprietary_files(extracted_path)
            self._copy_proprietary_files(extracted_path, output_dir)
            self._generate_proprietary_files_txt(output_dir)
            self._generate_android_mk(output_dir)
            self._generate_android_bp(output_dir)
            self._generate_board_config(output_dir)
            self._generate_device_vendor_mk(output_dir)

            self.logger.info(
                "Generated vendor tree with %d proprietary files",
                len(self.proprietary_files),
            )
            return True
        except Exception as e:
            self.logger.error("Error generating vendor tree: %s", e)
            return False

    def _create_directory_structure(self, output_dir: str):
        base_path = Path(output_dir)
        directories = [
            base_path / "proprietary",
            base_path / "proprietary/bin",
            base_path / "proprietary/etc",
            base_path / "proprietary/lib",
            base_path / "proprietary/lib64",
            base_path / "proprietary/vendor/bin",
            base_path / "proprietary/vendor/etc",
            base_path / "proprietary/vendor/lib",
            base_path / "proprietary/vendor/lib64",
            base_path / "proprietary/vendor/firmware",
            base_path / "proprietary/system/lib",
            base_path / "proprietary/system/lib64",
            base_path / "proprietary/product/lib",
            base_path / "proprietary/product/lib64",
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        self.logger.info("Created directory structure in %s", output_dir)

    def _scan_proprietary_files(self, extracted_path: str):
        self.logger.info("Scanning for proprietary files...")

        for root, _, files in os.walk(extracted_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, extracted_path)

                if self._is_proprietary_file(rel_path):
                    file_info = get_file_info(file_path)
                    if file_info:
                        self.proprietary_files.append(
                            {
                                "source_path": file_path,
                                "relative_path": rel_path,
                                "info": file_info,
                            }
                        )

        self.logger.info("Found %d proprietary files", len(self.proprietary_files))

    def _is_proprietary_file(self, rel_path: str) -> bool:
        for pattern in self.proprietary_patterns.get("include_patterns", []):
            if any(p in rel_path for p in pattern.get("paths", [])):
                for exclude in self.proprietary_patterns.get("exclude_patterns", []):
                    if any(p in rel_path for p in exclude.get("paths", [])):
                        return False
                return True
        return False

    def _copy_proprietary_files(self, extracted_path: str, output_dir: str):
        self.logger.info("Copying proprietary files...")

        for file_info in self.proprietary_files:
            source = file_info["source_path"]
            rel_path = file_info["relative_path"]
            dest_path = os.path.join(output_dir, "proprietary", rel_path)
            dest_dir = os.path.dirname(dest_path)

            os.makedirs(dest_dir, exist_ok=True)

            try:
                shutil.copy2(source, dest_path)
                if is_elf_file(source):
                    os.chmod(dest_path, 0o755)
            except Exception as e:
                self.logger.warning("Failed to copy %s: %s", rel_path, e)

    def _generate_proprietary_files_txt(self, output_dir: str):
        output_file = os.path.join(output_dir, "proprietary-files.txt")

        with open(output_file, "w") as f:
            f.write(f"# Proprietary files for {self.vendor_name} {self.device_name}\n")
            f.write("# Generated by vendor_tree_generator\n\n")

            partitions = {}
            for file_info in self.proprietary_files:
                rel_path = file_info["relative_path"]
                partition = rel_path.split("/")[0] if "/" in rel_path else "system"
                partitions.setdefault(partition, []).append(rel_path)

            for partition in sorted(partitions.keys()):
                if partition != "system":
                    f.write(f"\n# {partition.upper()} files\n")
                for file_path in sorted(partitions[partition]):
                    f.write(f"{file_path}\n")

        self.logger.info("Generated proprietary-files.txt with %d files", len(self.proprietary_files))

    def _generate_android_mk(self, output_dir: str):
        output_file = os.path.join(output_dir, "Android.mk")
        content = self.templates.generate_android_mk(self.proprietary_files)
        with open(output_file, "w") as f:
            f.write(content)
        self.logger.info("Generated Android.mk")

    def _generate_android_bp(self, output_dir: str):
        output_file = os.path.join(output_dir, "Android.bp")
        content = self.templates.generate_android_bp(self.proprietary_files)
        with open(output_file, "w") as f:
            f.write(content)
        self.logger.info("Generated Android.bp")

    def _generate_board_config(self, output_dir: str):
        output_file = os.path.join(output_dir, "BoardConfig.mk")
        content = self.templates.generate_board_config()
        with open(output_file, "w") as f:
            f.write(content)
        self.logger.info("Generated BoardConfig.mk")

    def _generate_device_vendor_mk(self, output_dir: str):
        output_file = os.path.join(output_dir, f"{self.device_name}-vendor.mk")
        content = self.templates.generate_device_vendor_mk(self.proprietary_files)
        with open(output_file, "w") as f:
            f.write(content)
        self.logger.info("Generated %s-vendor.mk", self.device_name)

    def _load_proprietary_patterns(self) -> Dict:
        config_file = Path(__file__).resolve().parent / "config" / "proprietary_patterns.json"

        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except Exception:
            return {
                "include_patterns": [
                    {"paths": ["vendor/bin/", "vendor/lib/", "vendor/lib64/", "vendor/etc/", "vendor/firmware/"]},
                    {"paths": ["system/lib/", "system/lib64/"]},
                    {"paths": ["product/lib/", "product/lib64/"]},
                    {"paths": ["bin/"]},
                ],
                "exclude_patterns": [
                    {"paths": [".txt", ".xml", ".conf", ".cfg", ".ini", ".json"]},
                ],
            }
