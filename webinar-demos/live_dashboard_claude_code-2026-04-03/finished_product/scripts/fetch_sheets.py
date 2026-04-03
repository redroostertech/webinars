"""Standalone script: fetch Google Sheets data into data/sheets_raw.json."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from repositories.data_repository import DataRepository
from services.sheets_service import SheetsService


def main():
    print("Fetching Google Sheets data...")

    sheets = SheetsService(Config.CREDENTIALS_PATH, Config.TOKEN_PATH)
    repo = DataRepository(Config.DATA_DIR)

    raw = sheets.fetch(Config.GOOGLE_SHEET_ID)
    repo.save_sheets_raw(raw)

    row_count = len(raw.get("rows", []))
    print(f"Done. {row_count} rows saved to data/sheets_raw.json")


if __name__ == "__main__":
    main()
