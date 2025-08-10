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

---

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
