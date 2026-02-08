# Image Operations

**image_operations** is a modular, extensible suite of command-line tools for managing, organizing, and cleaning up your photo library. It includes powerful utilities for finding duplicate images, resizing, format conversion, and metadata extraction.

---

## Features

- Find and remove or move duplicate images using perceptual hashing
- Automatically keep the best-quality version based on resolution and file size
- Resize images for web or social media use
- Convert images between popular formats (JPG, PNG, WEBP, etc.)
- Extract and export image metadata (EXIF: date, location, camera, etc.)
- Organize photos into folders by date
- Safe, scriptable, and extensible with dry-run options and logging

---

## Installation

### Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`
- To update: use `pip freeze > requirements.txt`

### Setup

Clone the repo and install dependencies in a virtual environment:

```bash
git clone ..
cd imageoperations
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You can run individual tools directly or install the package for CLI access:

```bash
pip install .
```

---

## Tools Overview

### 1. `find_duplicates.py`

Recursively scans a folder for duplicate images using perceptual hashing.

**Usage:**

```bash
python find_duplicates.py /path/to/images
```

**Options:**

- `--move`: Move duplicates to a `duplicates/` folder
- `--delete`: Permanently delete duplicates

**Example:**

```bash
python find_duplicates.py ~/Pictures --move
```

### 2. `download_dropbox.py`
This script downloads your Dropbox files to a local folder.
It can download your entire Dropbox or just a specific folder.
A dry run mode is also provided to preview file names and sizes without downloading

1. Set your dropbox access token
Generate an access token from the Dropbox App Console:

https://www.dropbox.com/developers/apps

Then set it in your terminal:

```bash
export DROPBOX_ACCESS_TOKEN="sl.your_token_here"
```

---

### 2. Basic Usage (download everything)

```bash
python download_dropbox.py
```

Your files will be mirrored into:

```
./dropbox_backup/
```

---

### 3. Download a Specific Folder

```bash
python download_dropbox.py --remote-folder "/Photos/2020"
```

This will recreate the folder structure locally under your `--local-root` path.

---

### 4. Dry Run (list files and sizes without downloading)

```bash
python download_dropbox.py --dry-run
```

Or for a specific folder:

```bash
python download_dropbox.py --remote-folder "/Documents" --dry-run
```

---

### 5. Additional Options

| Option                      | Description |
|-----------------------------|-------------|
| `--local-root PATH`         | Destination folder (default: `./dropbox_backup`) |
| `--remote-folder "/path"`   | Only download a specific Dropbox folder |
| `--skip-existing-same-size` | Skip files already downloaded with matching size |
| `--dry-run`                 | List everything without downloading |

Example:

```bash
python download_dropbox.py \
  --remote-folder "/Photos" \
  --local-root "./backup_photos" \
  --skip-existing-same-size
```
---
3. compare_folders.py

Performs a "deep" comparison between two directories (including subdirectories) to identify images present in the Source that are missing from the Target.

This tool uses Perceptual Hashing (pHash), meaning it identifies images that look the same even if they have different filenames, compression levels, or dimensions.

Usage:

```Bash
python compare_folders.py /path/to/source /path/to/target [options]
Options:

Option	Description
--sync	Copies missing files from Source to Target, maintaining the sub-directory structure.
--dry-run	Used with --sync. Shows which files would be copied without actually moving data.
```
Example:

```Bash
# Just list missing images
python compare_folders.py ./Master_Photos ./Backup_Photos

# Preview a sync operation
python compare_folders.py ./Master_Photos ./Backup_Photos --sync --dry-run

# Execute the sync
python compare_folders.py ./Master_Photos ./Backup_Photos --sync
```
__
## Roadmap

- Configurable perceptual hash algorithm (aHash, pHash, dHash, etc.)
- Format-aware deduplication (e.g., prefer PNG over JPG)
- Optional GUI or TUI
- Smart tagging or grouping based on metadata
- GPhoto2 or external device import support

---

## Contributing

Pull requests are welcome! If you’d like to contribute, please:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/tool-name`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## License

MIT License

---

## Disclaimer

Always use the `--dry-run` or empty flag before running destructive commands like `--delete`. This project comes with no warranties — use at your own risk.
