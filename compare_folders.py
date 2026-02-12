import os
import sys
import shutil
from PIL import Image
import imagehash
import pillow_heif

pillow_heif.register_heif_opener()

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.heic', '.webp')

def get_image_hash(filepath):
    try:
        with Image.open(filepath) as img:
            return str(imagehash.phash(img))
    except Exception as e:
        print(f"  [Error] Could not process {filepath}: {e}")
        return None

def scan_directory(directory, verbose=False):
    hash_map = {}
    print(f"🔍 Scanning directory: {directory}")
    count = 0
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(IMAGE_EXTENSIONS):
                count += 1
                path = os.path.join(root, filename)
                
                if verbose:
                    print(f"  [{count}] Indexing: {path}")
                elif count % 50 == 0: # Small progress indicator for non-verbose
                    print(f"  ...indexed {count} images", end='\r')

                h = get_image_hash(path)
                if h and h not in hash_map:
                    hash_map[h] = path
            else:
                if verbose:
                    print(f"skipping {filename}")
    print(f"\n✅ Scan complete. Total images indexed: {count}")
    return hash_map

def main():
    if len(sys.argv) < 3:
        print("Usage: python compare_folders.py <source_dir> <target_dir> [--sync] [--dry-run] [--verbose]")
        sys.exit(1)

    source_dir = os.path.abspath(sys.argv[1])
    target_dir = os.path.abspath(sys.argv[2])
    sync_enabled = '--sync' in sys.argv
    dry_run = '--dry-run' in sys.argv
    verbose = '--verbose' in sys.argv

    # 1. Map Source and Target
    source_map = scan_directory(source_dir, verbose=verbose)
    target_map = scan_directory(target_dir, verbose=verbose)

    # 2. Identify missing items
    missing_items = []
    for h, source_path in source_map.items():
        if h not in target_map:
            missing_items.append(source_path)

    # 3. Report and Execute
    print("\n" + "="*60)
    if not missing_items:
        print("✅ Success: Target contains all images found in Source.")
    else:
        print(f"Found {len(missing_items)} images in Source missing from Target.")
        
        for source_path in missing_items:
            rel_path = os.path.relpath(source_path, source_dir)
            dest_path = os.path.join(target_dir, rel_path)

            if sync_enabled:
                prefix = "[DRY RUN] Would copy" if dry_run else "🚀 Copying"
                print(f"{prefix}: {rel_path}")
                
                if not dry_run:
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(source_path, dest_path)
            else:
                print(f"📍 Missing: {rel_path}")

    if dry_run:
        print("\n[NOTE] This was a dry run. No files were actually copied.")
    print("="*60)

if __name__ == "__main__":
    main()