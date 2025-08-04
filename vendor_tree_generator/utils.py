#!/usr/bin/env python3

import os
import subprocess
import logging
import hashlib
from typing import Optional, Dict
from pathlib import Path

def setup_logging(level: int = logging.INFO):
    """Setup logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def check_dependencies() -> bool:
    """Check if required dependencies are available."""
    required_tools = ['lpunpack', 'simg2img', 'mount', 'sudo']
    
    for tool in required_tools:
        if not which(tool):
            logging.error(f"Required tool not found: {tool}")
            return False
    
    return True

def which(program: str) -> Optional[str]:
    """Find executable in PATH."""
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ.get("PATH", "").split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def get_file_info(file_path: str) -> Optional[Dict]:
    """Get file information including size and type."""
    try:
        stat = os.stat(file_path)
        
        info = {
            'size': stat.st_size,
            'mode': oct(stat.st_mode),
            'is_executable': os.access(file_path, os.X_OK),
            'is_elf': is_elf_file(file_path),
            'sha1': calculate_sha1(file_path)
        }
        
        return info
        
    except Exception:
        return None

def is_elf_file(file_path: str) -> bool:
    """Check if file is an ELF binary."""
    try:
        with open(file_path, 'rb') as f:
            magic = f.read(4)
            return magic == b'\x7fELF'
    except Exception:
        return False

def calculate_sha1(file_path: str) -> str:
    """Calculate SHA1 hash of file."""
    try:
        hash_sha1 = hashlib.sha1()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha1.update(chunk)
        return hash_sha1.hexdigest()
    except Exception:
        return ""
