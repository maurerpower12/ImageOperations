import os

# --- Configuration ---
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')

def count_images(folder_path):
    count = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.lower().endswith(IMAGE_EXTENSIONS):
                count += 1
    return count

# --- CLI Usage ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python count_images.py /path/to/folder")
        sys.exit(1)

    path = sys.argv[1]

    if not os.path.exists(path) or not os.path.isdir(path):
        print(f"Error: '{path}' is not a valid directory.")
        sys.exit(1)

    total = count_images(path)
    print(f"Total image files found: {total}")
