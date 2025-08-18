import os
import shutil
import sys

def flatten_directory(root_path, dry_run=False):
    file_counter = 0
    conflict_counter = 0

    for dirpath, _, filenames in os.walk(root_path):
        # Skip the root itself
        if os.path.abspath(dirpath) == os.path.abspath(root_path):
            continue

        for filename in filenames:
            original_path = os.path.join(dirpath, filename)
            destination_path = os.path.join(root_path, filename)

            # Avoid overwriting by appending a number
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(destination_path):
                destination_path = os.path.join(root_path, f"{base}_{counter}{ext}")
                counter += 1
                conflict_counter += 1

            if dry_run:
                print(f"[Dry Run] Would move: {original_path} → {destination_path}")
            else:
                try:
                    shutil.move(original_path, destination_path)
                    print(f"Moved: {original_path} → {destination_path}")
                    file_counter += 1
                except Exception as e:
                    print(f"Error moving {original_path}: {e}")

    print("\n--- Summary ---")
    print(f"{'[Dry Run] ' if dry_run else ''}Total files processed: {file_counter}")
    if dry_run:
        print(f"Filename conflicts simulated: {conflict_counter}")

# --- CLI Usage ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python flatten_folder.py /path/to/folder [--dry-run]")
        sys.exit(1)

    root_dir = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    if not os.path.isdir(root_dir):
        print(f"Error: {root_dir} is not a directory.")
        sys.exit(1)

    flatten_directory(root_dir, dry_run)