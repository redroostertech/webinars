"""Standalone script: run the full ETL pipeline end to end."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.drive_service import DriveService
from services.sheets_service import SheetsService
from services.openai_service import OpenAIService
from services.etl_service import ETLService


def main():
    print("Running full ETL pipeline...")
    print("  1. Scan Google Drive folders")
    print("  2. Read new spreadsheets")
    print("  3. Normalize with OpenAI")
    print("  4. Reconcile cross-references")
    print("  5. Write back to master Google Sheet")
    print()

    drive = DriveService()
    sheets = SheetsService()
    openai_svc = OpenAIService()
    etl = ETLService(drive, sheets, openai_svc)

    results = etl.run_full_pipeline()

    print(f"Status: {results['status']}")
    print(f"Files processed: {results['files_processed']}")
    print(f"Records added: {results['records_added']}")
    print(f"Timestamp: {results['timestamp']}")

    if results["errors"]:
        print("\nErrors:")
        for error in results["errors"]:
            print(f"  - {error}")
    else:
        print("\nNo errors. Pipeline complete.")


if __name__ == "__main__":
    main()
