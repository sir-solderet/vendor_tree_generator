#!/usr/bin/env python3

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Set
from .templates import VendorTreeTemplates
from .utils import get_file_info, is_elf_file, calculate_sha1

class VendorTreeGenerator:
    """Generates vendor tree structure and files."""
    
    def __init__(self, vendor_name: str, device_name: str, 
                 android_version: str = "13", verbose: bool = False):
        self.vendor_name = vendor_name
        self.device_name = device_name
        self.android_version = android_version
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        self.templates = VendorTreeTemplates(vendor_name, device_name, android_version)
        
        # Load proprietary file patterns
        self.proprietary_patterns = self._load_proprietary_patterns()
        self.found_files = []
        self.proprietary_files = []
    
    def generate_tree(self, extracted_path: str, output_dir: str) -> bool:
        """Generate the complete vendor tree."""
        try:
            # Create output directory structure
            self._create_directory_structure(output_dir)
            
            # Scan for proprietary files
            self._scan_proprietary_files(extracted_path)
            
            # Copy proprietary files
            self._copy_proprietary_files(extracted_path, output_dir)
            
            # Generate proprietary-files.txt
            self._generate_proprietary_files_txt(output_dir)
            
            # Generate Android.mk
            self._generate_android_mk(output_dir)
            
            # Generate Android.bp
            self._generate_android_bp(output_dir)
            
            # Generate BoardConfig.mk
            self._generate_board_config(output_dir)
            
            # Generate device-vendor.mk
            self._generate_device_vendor_mk(output_dir)
            
            self.logger.info(f"Generated vendor tree with {len(self.proprietary_files)} proprietary files")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating vendor tree: {e}")
            return False
    
    def _create_directory_structure(self, output_dir: str):
        """Create the vendor tree directory structure."""
        base_path = Path(output_dir)
        
        # Create main directories
        directories = [
            base_path,
            base_path / "proprietary",
            base_path / "proprietary" / "bin",
            base_path / "proprietary" / "etc",
            base_path / "proprietary" / "lib",
            base_path / "proprietary" / "lib64",
            base_path / "proprietary" / "vendor" / "bin",
            base_path / "proprietary" / "vendor" / "etc",
            base_path / "proprietary" / "vendor" / "lib",
            base_path / "proprietary" / "vendor" / "lib64",
            base_path / "proprietary" / "vendor" / "firmware",
            base_path / "proprietary" / "system" / "lib",
            base_path / "proprietary" / "system" / "lib64",
            base_path / "proprietary" / "product" / "lib",
            base_path / "proprietary" / "product" / "lib64",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Created directory structure in {output_dir}")
    
    def _scan_proprietary_files(self, extracted_path: str):
        """Scan extracted files for proprietary blobs."""
        self.logger.info("Scanning for proprietary files...")
        
        for root, dirs, files in os.walk(extracted_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, extracted_path)
                
                # Check if file matches proprietary patterns
                if self._is_proprietary_file(rel_path):
                    file_info = get_file_info(file_path)
                    if file_info:
                        self.proprietary_files.append({
                            'source_path': file_path,
                            'relative_path': rel_path,
                            'info': file_info
                        })
        
        self.logger.info(f"Found {len(self.proprietary_files)} proprietary files")
    
    def _is_proprietary_file(self, rel_path: str) -> bool:
        """Check if a file is proprietary based on patterns."""
        # Check against patterns
        for pattern in self.proprietary_patterns.get('include_patterns', []):
            if any(p in rel_path for p in pattern.get('paths', [])):
                # Check exclusions
                excluded = False
                for exclude_pattern in self.proprietary_patterns.get('exclude_patterns', []):
                    if any(p in rel_path for p in exclude_pattern.get('paths', [])):
                        excluded = True
                        break
                
                if not excluded:
                    return True
        
        return False
    
    def _copy_proprietary_files(self, extracted_path: str, output_dir: str):
        """Copy proprietary files to vendor tree."""
        self.logger.info("Copying proprietary files...")
        
        for file_info in self.proprietary_files:
            source = file_info['source_path']
            rel_path = file_info['relative_path']
            
            # Determine destination path
            dest_path = os.path.join(output_dir, "proprietary", rel_path)
            dest_dir = os.path.dirname(dest_path)
            
            # Create destination directory
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copy file
            try:
                import shutil
                shutil.copy2(source, dest_path)
                
                # Preserve permissions for binaries
                if is_elf_file(source):
                    os.chmod(dest_path, 0o755)
                    
            except Exception as e:
                self.logger.warning(f"Failed to copy {rel_path}: {e}")
    
    def _generate_proprietary_files_txt(self, output_dir: str):
        """Generate proprietary-files.txt."""
        output_file = os.path.join(output_dir, "proprietary-files.txt")
        
        with open(output_file, 'w') as f:
            f.write(f"# Proprietary files for {self.vendor_name} {self.device_name}\n")
            f.write(f"# Generated by vendor_tree_generator\n\n")
            
            # Group files by partition
            partitions = {}
            for file_info in self.proprietary_files:
                rel_path = file_info['relative_path']
                partition = rel_path.split('/')[0] if '/' in rel_path else 'system'
                
                if partition not in partitions:
                    partitions[partition] = []
                partitions[partition].append(rel_path)
            
            # Write files grouped by partition
            for partition in sorted(partitions.keys()):
                if partition != 'system':
                    f.write(f"\n# {partition.upper()} files\n")
                
                for file_path in sorted(partitions[partition]):
                    f.write(f"{file_path}\n")
        
        self.logger.info(f"Generated proprietary-files.txt with {len(self.proprietary_files)} files")
    
    def _generate_android_mk(self, output_dir: str):
        """Generate Android.mk."""
        output_file = os.path.join(output_dir, "Android.mk")
        content = self.templates.generate_android_mk(self.proprietary_files)
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        self.logger.info("Generated Android.mk")
    
    def _generate_android_bp(self, output_dir: str):
        """Generate Android.bp."""
        output_file = os.path.join(output_dir, "Android.bp")
        content = self.templates.generate_android_bp(self.proprietary_files)
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        self.logger.info("Generated Android.bp")
    
    def _generate_board_config(self, output_dir: str):
        """Generate BoardConfig.mk."""
        output_file = os.path.join(output_dir, "BoardConfig.mk")
        content = self.templates.generate_board_config()
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        self.logger.info("Generated BoardConfig.mk")
    
    def _generate_device_vendor_mk(self, output_dir: str):
        """Generate device-vendor.mk."""
        output_file = os.path.join(output_dir, f"{self.device_name}-vendor.mk")
        content = self.templates.generate_device_vendor_mk(self.proprietary_files)
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        self.logger.info(f"Generated {self.device_name}-vendor.mk")
    
    def _load_proprietary_patterns(self) -> Dict:
        """Load proprietary file patterns from config."""
        config_file = Path(__file__).parent.parent / "config" / "proprietary_patterns.json"
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception:
            # Return default patterns if config file not found
            return {
                "include_patterns": [
                    {"paths": ["vendor/bin/", "vendor/lib/", "vendor/lib64/", "vendor/etc/", "vendor/firmware/"]},
                    {"paths": ["system/lib/", "system/lib64/"]},
                    {"paths": ["product/lib/", "product/lib64/"]},
                    {"paths": ["bin/"]},
                ],
                "exclude_patterns": [
                    {"paths": [".txt", ".xml", ".conf", ".cfg", ".ini", ".json"]},
                ]
            }
