#!/usr/bin/env python3

import os
import subprocess
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Optional


class ImageExtractor:
    """Handles extraction of super.img and partition images."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        self.temp_dirs = []
        self.mounted_dirs = []

    def extract_super_img(self, super_img_path: str) -> Optional[str]:
        """Extract super.img using lpunpack."""
        try:
            temp_dir = tempfile.mkdtemp(prefix="vendor_tree_super_")
            self.temp_dirs.append(temp_dir)

            self.logger.info(f"Extracting super.img to {temp_dir}")
            cmd = ["lpunpack", super_img_path, temp_dir]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                self.logger.error(f"lpunpack failed: {result.stderr}")
                return None

            expected_partitions = [
                "vendor.img",
                "system.img",
                "product.img",
                "system_ext.img",
            ]
            found_partitions = []

            for partition in expected_partitions:
                partition_path = os.path.join(temp_dir, partition)
                if os.path.exists(partition_path):
                    found_partitions.append(partition)

            if not found_partitions:
                self.logger.error("No expected partitions found in super.img")
                return None

            self.logger.info(f"Found partitions: {', '.join(found_partitions)}")

            extracted_dir = tempfile.mkdtemp(prefix="vendor_tree_extracted_")
            self.temp_dirs.append(extracted_dir)

            for partition in found_partitions:
                partition_path = os.path.join(temp_dir, partition)
                self._extract_partition(
                    partition_path, extracted_dir, partition.replace(".img", "")
                )

            return extracted_dir

        except Exception as e:
            self.logger.error(f"Error extracting super.img: {e}")
            return None

    def extract_partition_img(self, partition_img_path: str) -> Optional[str]:
        """Extract a single partition image."""
        try:
            extracted_dir = tempfile.mkdtemp(prefix="vendor_tree_partition_")
            self.temp_dirs.append(extracted_dir)

            partition_name = Path(partition_img_path).stem
            self.logger.info(f"Extracting partition: {partition_name}")

            success = self._extract_partition(
                partition_img_path, extracted_dir, partition_name
            )

            return extracted_dir if success else None

        except Exception as e:
            self.logger.error(f"Error extracting partition image: {e}")
            return None

    def _extract_partition(
        self, img_path: str, output_dir: str, partition_name: str
    ) -> bool:
        """Extract a single partition image file."""
        try:
            converted_img = self._convert_sparse_image(img_path)
            if not converted_img:
                converted_img = img_path

            mount_point = tempfile.mkdtemp(prefix=f"mount_{partition_name}_")
            self.mounted_dirs.append(mount_point)

            cmd = ["sudo", "mount", "-o", "loop,ro", converted_img, mount_point]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                self.logger.warning(f"Failed to mount {partition_name}: {result.stderr}")
                return False

            partition_output = os.path.join(output_dir, partition_name)
            os.makedirs(partition_output, exist_ok=True)

            self.logger.info(f"Copying {partition_name} files...")
            cmd = ["sudo", "cp", "-r", f"{mount_point}/.", partition_output]
            result = subprocess.run(cmd, capture_output=True, text=True)

            subprocess.run(["sudo", "umount", mount_point], capture_output=True)

            if result.returncode == 0:
                self.logger.info(f"Successfully extracted {partition_name}")
                return True
            else:
                self.logger.error(f"Failed to copy {partition_name} files: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error extracting partition {partition_name}: {e}")
            return False

    def _convert_sparse_image(self, img_path: str) -> Optional[str]:
        """Convert sparse image to raw image using simg2img."""
        try:
            with open(img_path, "rb") as f:
                magic = f.read(4)
                if magic != b"\x3a\xff\x26\xed":
                    return None

            temp_raw = tempfile.mktemp(suffix=".raw.img")
            cmd = ["simg2img", img_path, temp_raw]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                self.logger.info(f"Converted sparse image: {os.path.basename(img_path)}")
                return temp_raw
            else:
                self.logger.warning(f"Failed to convert sparse image: {result.stderr}")
                return None

        except Exception as e:
            self.logger.error(f"Error converting sparse image: {e}")
            return None

    def cleanup(self):
        """Clean up temporary directories and unmount any mounted filesystems."""
        for mount_point in self.mounted_dirs:
            try:
                subprocess.run(
                    ["sudo", "umount", mount_point], capture_output=True, timeout=10
                )
                if os.path.exists(mount_point):
                    os.rmdir(mount_point)
            except Exception:
                pass

        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception:
                pass

        self.temp_dirs.clear()
        self.mounted_dirs.clear()
