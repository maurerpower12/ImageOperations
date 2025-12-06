import os
import sys
import time
import argparse
from typing import Optional, Tuple

import dropbox
from dropbox.files import FileMetadata, FolderMetadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download all files (or a subfolder) from Dropbox to local disk."
    )
    parser.add_argument(
        "--access-token",
        help=(
            "Dropbox API access token. "
            "If not provided, uses environment variable DROPBOX_ACCESS_TOKEN."
        ),
    )
    parser.add_argument(
        "--local-root",
        default="dropbox_backup",
        help="Local root folder where files will be stored (default: ./dropbox_backup).",
    )
    parser.add_argument(
        "--remote-folder",
        default="",
        help=(
            "Dropbox folder to download (e.g. '/Photos/2020'). "
            "Default: '' (entire Dropbox)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not download anything; just list files and sizes.",
    )
    parser.add_argument(
        "--skip-existing-same-size",
        action="store_true",
        help="Skip files that already exist locally with the same size.",
    )
    return parser.parse_args()


def get_access_token(cli_token: Optional[str]) -> str:
    token = cli_token or os.getenv("DROPBOX_ACCESS_TOKEN")
    if not token:
        print(
            "ERROR: No access token provided.\n"
            "Provide one with --access-token or set DROPBOX_ACCESS_TOKEN env var."
        )
        sys.exit(1)
    return token


def normalize_remote_folder(path: str) -> str:
    """
    Normalize the remote folder path for Dropbox API:
    - '' means root
    - strip trailing slashes
    - ensure it starts with '/' if not empty
    """
    path = path.strip()
    if path in ("", "/"):
        return ""
    if not path.startswith("/"):
        path = "/" + path
    # Dropbox API is fine with a leading slash; we'll keep it
    # but remove a trailing slash if present
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return path


def create_local_path(local_root: str, dropbox_path: str, remote_base: str) -> str:
    """
    Map a Dropbox path like '/folder/sub/file.txt' to a local path under local_root.
    If remote_base is not '', paths are made relative to that base.

    Example:
        local_root = /backup
        remote_base = /Photos
        dropbox_path = /Photos/2020/img.jpg
        -> /backup/2020/img.jpg
    """
    # Normalize
    dropbox_path = dropbox_path.lower()  # safe: Dropbox paths are case-insensitive
    remote_base = remote_base.lower()

    if remote_base and dropbox_path.startswith(remote_base):
        relative = dropbox_path[len(remote_base):]
    else:
        relative = dropbox_path

    relative = relative.lstrip("/")
    return os.path.join(local_root, relative)


def download_file(
    dbx: dropbox.Dropbox,
    metadata: FileMetadata,
    local_root: str,
    remote_base: str,
    dry_run: bool,
    skip_existing_same_size: bool,
) -> Tuple[int, int]:
    """
    Download a single file from Dropbox to local filesystem (unless dry_run).

    Returns:
        (file_count, bytes_count) for this file (0 if skipped).
    """
    dropbox_path = metadata.path_lower
    local_path = create_local_path(local_root, dropbox_path, remote_base)

    # Make sure local directory exists
    local_dir = os.path.dirname(local_path)
    os.makedirs(local_dir, exist_ok=True)

    if dry_run:
        print(f"[FILE] {dropbox_path} ({metadata.size} bytes)")
        return 1, metadata.size

    # Simple resume/skip logic
    if skip_existing_same_size and os.path.exists(local_path):
        local_size = os.path.getsize(local_path)
        if local_size == metadata.size:
            print(f"[SKIP] {dropbox_path} (already downloaded, size matches)")
            return 0, 0

    print(f"[GET ] {dropbox_path} -> {local_path}")
    try:
        with open(local_path, "wb") as f:
            _, res = dbx.files_download(path=metadata.path_lower)
            f.write(res.content)
        return 1, metadata.size
    except Exception as e:
        print(f"  !! Error downloading {dropbox_path}: {e}")
        return 0, 0


def walk_folder(
    dbx: dropbox.Dropbox,
    folder_path: str,
    local_root: str,
    remote_base: str,
    dry_run: bool,
    skip_existing_same_size: bool,
) -> Tuple[int, int]:
    """
    Recursively walk a Dropbox folder and process all files.

    Returns:
        (total_files, total_bytes)
    """
    total_files = 0
    total_bytes = 0

    # Normalize root folder
    if folder_path in ("", "/"):
        display_path = "/"
    else:
        display_path = folder_path

    print(f"[LIST] folder: {display_path}")

    try:
        result = dbx.files_list_folder(path=folder_path, recursive=False)
    except dropbox.exceptions.ApiError as e:
        print(f"  !! API error listing '{folder_path}': {e}")
        return 0, 0

    while True:
        for entry in result.entries:
            if isinstance(entry, FolderMetadata):
                # Recreate folder locally for non-dry-run; safe to call even in dry-run
                local_folder = create_local_path(local_root, entry.path_lower, remote_base)
                os.makedirs(local_folder, exist_ok=True)
                # Recurse into subfolder
                f_count, b_count = walk_folder(
                    dbx,
                    entry.path_lower,
                    local_root,
                    remote_base,
                    dry_run,
                    skip_existing_same_size,
                )
                total_files += f_count
                total_bytes += b_count

            elif isinstance(entry, FileMetadata):
                f_count, b_count = download_file(
                    dbx,
                    entry,
                    local_root,
                    remote_base,
                    dry_run,
                    skip_existing_same_size,
                )
                total_files += f_count
                total_bytes += b_count

            else:
                # Could be deleted or other metadata types
                print(f"[SKIP] unsupported entry type: {entry}")

        if result.has_more:
            print("  ... more items, continuing")
            try:
                result = dbx.files_list_folder_continue(result.cursor)
            except dropbox.exceptions.ApiError as e:
                print(f"  !! Error continuing listing: {e}")
                break
        else:
            break

    return total_files, total_bytes


def main():
    args = parse_args()

    access_token = get_access_token(args.access_token)
    local_root = os.path.abspath(args.local_root)
    remote_folder = normalize_remote_folder(args.remote_folder)

    print(f"Local backup root: {local_root}")
    print(f"Remote folder: {remote_folder or '/'}")
    print(f"Dry run: {args.dry_run}")
    print(f"Skip existing same size: {args.skip_existing_same_size}")
    print("")

    os.makedirs(local_root, exist_ok=True)

    # Initialize client
    dbx = dropbox.Dropbox(access_token)

    # Sanity check: who am I?
    try:
        acct = dbx.users_get_current_account()
        print(f"Connected to Dropbox account: {acct.name.display_name} ({acct.email})")
    except Exception as e:
        print("ERROR: Could not verify Dropbox token / account.")
        print(e)
        sys.exit(1)

    start = time.time()

    total_files, total_bytes = walk_folder(
        dbx,
        remote_folder,
        local_root,
        remote_base=remote_folder,
        dry_run=args.dry_run,
        skip_existing_same_size=args.skip_existing_same_size,
    )

    elapsed = time.time() - start

    print("\n======== SUMMARY ========")
    print(f"Files {'found' if args.dry_run else 'downloaded'}: {total_files}")
    print(f"Total bytes: {total_bytes} (~{total_bytes / (1024**3):.2f} GB)")
    print(f"Elapsed time: {elapsed:.1f}s")
    print(f"Local backup root: {local_root}")
    print("=========================\n")


if __name__ == "__main__":
    main()