import os
import sys
import shutil
from PIL import Image
import imagehash
from collections import defaultdict

# ----- Parse Arguments -----
if len(sys.argv) < 2:
    print("Usage: python find_duplicates.py /path/to/images [--move | --delete]")
    sys.exit(1)

ROOT_FOLDER = sys.argv[1]
MOVE_DUPLICATES = '--move' in sys.argv
DELETE_DUPLICATES = '--delete' in sys.argv
DUPLICATES_FOLDER = os.path.join(ROOT_FOLDER, 'duplicates')

if MOVE_DUPLICATES and DELETE_DUPLICATES:
    print("Error: You cannot use both --move and --delete at the same time.")
    sys.exit(1)

# ----- Settings -----
hashes = defaultdict(list)
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')

# ----- Function to Find and Handle Duplicates -----
def find_duplicate_images(root_folder):
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith(IMAGE_EXTENSIONS):
                filepath = os.path.join(dirpath, filename)
                try:
                    with Image.open(filepath) as img:
                        hash_val = imagehash.average_hash(img)
                        hashes[str(hash_val)].append(filepath)
                except Exception as e:
                    print(f"Could not process {filepath}: {e}")

    duplicates_found = False
    for hash_val, files in hashes.items():
        if len(files) > 1:
            duplicates_found = True

            # Choose best image by resolution → file size
            best_file = select_best_quality(files)
            print(f"\nDuplicate images found for hash {hash_val}:")
            print(f" - [KEEP] {best_file}")

            for f in files:
                if f != best_file:
                    print(f" - [DUPLICATE] {f}")
                    if MOVE_DUPLICATES:
                        move_to_duplicates(f)
                    elif DELETE_DUPLICATES:
                        delete_file(f)

    if not duplicates_found:
        print("No duplicate images found.")

# ----- Move File to "duplicates" Folder -----
def move_to_duplicates(filepath):
    if not os.path.exists(DUPLICATES_FOLDER):
        os.makedirs(DUPLICATES_FOLDER)

    filename = os.path.basename(filepath)
    destination = os.path.join(DUPLICATES_FOLDER, filename)

    # Ensure no overwriting
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(destination):
        destination = os.path.join(DUPLICATES_FOLDER, f"{base}_{counter}{ext}")
        counter += 1

    try:
        shutil.move(filepath, destination)
        print(f"    ↳ Moved to: {destination}")
    except Exception as e:
        print(f"    ✗ Could not move {filepath}: {e}")

# ----- Delete File Permanently -----
def delete_file(filepath):
    try:
        os.remove(filepath)
        print(f"    🗑️ Deleted: {filepath}")
    except Exception as e:
        print(f"    ✗ Could not delete {filepath}: {e}")

# ----- Select Best Quality Image -----
def select_best_quality(filepaths):
    def score(filepath):
        try:
            with Image.open(filepath) as img:
                width, height = img.size
                resolution = width * height
            filesize = os.path.getsize(filepath)
            return (resolution, filesize)
        except Exception:
            return (0, 0)  # In case of unreadable file

    # Sort by resolution, then file size (both descending)
    return max(filepaths, key=score)

# ----- Run -----
find_duplicate_images(ROOT_FOLDER)