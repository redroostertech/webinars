"""Standalone script: normalize raw Drive data and reconcile with existing Sheets."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.drive_service import DriveService
from services.sheets_service import SheetsService
from services.openai_service import OpenAIService


def main():
    print("Normalizing and reconciling data...")

    drive = DriveService()
    sheets = SheetsService()
    openai_svc = OpenAIService()

    # Scan all folders for files
    new_files = drive.scan_all_folders()

    for object_type, files in new_files.items():
        print(f"\nProcessing {object_type} ({len(files)} files)...")
        for file_info in files:
            try:
                headers, rows = drive.read_spreadsheet(file_info["id"])
                if not headers or not rows:
                    print(f"  Skipping {file_info['name']} (empty)")
                    continue

                normalized = openai_svc.normalize(headers, rows, object_type)
                print(f"  {file_info['name']}: {len(normalized)} records normalized")
            except Exception as e:
                print(f"  ERROR processing {file_info['name']}: {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
