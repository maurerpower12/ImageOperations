import sys
import os
from PIL import Image
from PIL.ExifTags import TAGS
import pillow_heif

# Enable HEIC support
pillow_heif.register_heif_opener()

def print_metadata(image_path):
    print("Insiden")
    if not os.path.exists(image_path):
        print(f"Error: File does not exist: {image_path}")
        return

    try:
        img = Image.open(image_path)
        exif_data = img.getexif()

        if not exif_data or len(exif_data) == 0:
            print("No EXIF metadata found.")
            return

        print(f"Metadata for: {image_path}\n")
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            print(f"{tag:25}: {value}")
    except Exception as e:
        print(f"Could not open or parse metadata: {e}")

# --- CLI usage ---
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python print_metadata.py /path/to/image")
        sys.exit(1)

    image_path = sys.argv[1]
    print_metadata(image_path)