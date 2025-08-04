import os
import subprocess
import magic


def is_elf_file(filepath: str) -> bool:
    """
    Check if a file is an ELF binary.
    """
    try:
        output = subprocess.check_output(["file", "--mime-type", "-b", filepath])
        return b"application/x-executable" in output or b"application/x-sharedlib" in output
    except Exception:
        return False


def get_file_info(filepath: str) -> dict:
    """
    Retrieve basic metadata about a file.
    """
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(filepath)

        size = os.path.getsize(filepath)

        return {
            "path": filepath,
            "mime_type": mime_type,
            "size": size,
        }
    except Exception as e:
        print(f"Error getting file info for {filepath}: {e}")
        return {}
