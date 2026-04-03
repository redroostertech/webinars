"""Standalone script: normalize raw data files into data/normalized.json."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from repositories.data_repository import DataRepository
from services.sheets_service import SheetsService
from services.reddit_service import RedditService
from services.etl_service import ETLService


def main():
    print("Normalizing data...")

    repo = DataRepository(Config.DATA_DIR)
    # ETLService needs these for extract, but we only use normalize here
    sheets_svc = SheetsService(Config.CREDENTIALS_PATH, Config.TOKEN_PATH)
    reddit_svc = RedditService(Config.APIFY_TOKEN)
    etl = ETLService(sheets_svc, reddit_svc, repo, Config)

    sheets_count, reddit_count = etl.normalize()
    print(
        f"Done. {sheets_count} Sheets rows + {reddit_count} Reddit posts "
        "written to data/normalized.json"
    )


if __name__ == "__main__":
    main()
