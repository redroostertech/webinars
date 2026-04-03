"""Standalone script: fetch Reddit data via Apify into data/reddit_raw.json."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from repositories.data_repository import DataRepository
from services.reddit_service import RedditService


def main():
    print(f"Fetching Reddit data from r/{Config.REDDIT_SUBREDDIT}...")

    reddit = RedditService(Config.APIFY_TOKEN)
    repo = DataRepository(Config.DATA_DIR)

    posts = reddit.fetch(Config.REDDIT_SUBREDDIT, max_items=25)
    repo.save_reddit_raw(posts)

    print(f"Done. {len(posts)} posts saved to data/reddit_raw.json")


if __name__ == "__main__":
    main()
