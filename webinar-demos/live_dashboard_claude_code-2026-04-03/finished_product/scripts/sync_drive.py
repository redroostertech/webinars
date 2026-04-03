"""Standalone script: scan Google Drive folders for new/updated spreadsheets."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.drive_service import DriveService


def main():
    print("Scanning Google Drive folders for new spreadsheets...")

    drive = DriveService()
    new_files = drive.scan_all_folders()

    for object_type, files in new_files.items():
        print(f"\n{object_type.upper()} folder: {len(files)} file(s)")
        for f in files:
            print(f"  - {f['name']} (modified: {f['modifiedTime']})")

    total = sum(len(files) for files in new_files.values())
    print(f"\nTotal: {total} spreadsheet(s) found across all folders.")


if __name__ == "__main__":
    main()
