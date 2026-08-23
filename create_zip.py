"""Script to package the complete JeevikaAI project into a clean ZIP archive."""

import os
import sys
import zipfile
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_ZIP = PROJECT_DIR.parent / "JeevikaAI_FINAL_PROJECT.zip"

EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git", ".system_generated", "venv", ".venv", "node_modules"}
EXCLUDE_EXTS = {".pyc", ".pyo", ".log", ".tmp"}

def create_archive():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print(f"Creating ZIP archive from: {PROJECT_DIR}")
    print(f"Target Output ZIP: {OUTPUT_ZIP}")

    included_files = []
    
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(PROJECT_DIR):
            # Exclude unwanted directories in-place
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                file_path = Path(root) / file
                
                # Check exclusions
                if file_path.suffix in EXCLUDE_EXTS:
                    continue
                if any(ex in file_path.parts for ex in EXCLUDE_DIRS):
                    continue
                if file == "create_zip.py":
                    continue

                rel_path = file_path.relative_to(PROJECT_DIR)
                zip_entry_name = Path("jeevika-ai") / rel_path
                zipf.write(file_path, arcname=str(zip_entry_name))
                included_files.append((str(rel_path), file_path.stat().st_size))

    zip_size_mb = OUTPUT_ZIP.stat().st_size / (1024 * 1024)
    print(f"\nZIP Archive Created Successfully!")
    print(f"Total Files Included: {len(included_files)}")
    print(f"Archive File Size: {zip_size_mb:.2f} MB ({OUTPUT_ZIP.stat().st_size:,} bytes)")
    print(f"Absolute Path: {OUTPUT_ZIP.resolve()}")

    # Print Category Breakdown
    print("\n--- ARCHIVE MANIFEST ---")
    for path, sz in sorted(included_files):
        print(f"  ✓ {path} ({sz:,} bytes)")

    return OUTPUT_ZIP, len(included_files), zip_size_mb

if __name__ == "__main__":
    create_archive()
