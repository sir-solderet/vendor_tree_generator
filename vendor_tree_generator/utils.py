import os
from pathlib import Path
import requests

GITHUB_RELEASE_BASE_URL = (
    "https://github.com/sir-solderet/vendor_tree_generator/releases/download"
)
RELEASE_TAG = "v1.0"  # or whatever tag you use

def download_images_if_needed(image_dir: Path, device: str):
    image_dir.mkdir(parents=True, exist_ok=True)
    partitions = [
        "vendor.img",
        "system.img",
        "product.img",
        "odm.img",
        "system_ext.img",
        "vendor_dlkm.img"
    ]

    for img in partitions:
        local_path = image_dir / img
        if local_path.exists():
            continue

        print(f"Downloading {img}...")
        url = f"{GITHUB_RELEASE_BASE_URL}/{RELEASE_TAG}/{img}"
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded {img}")
        else:
            print(f"Failed to download {img}. HTTP {response.status_code}")
