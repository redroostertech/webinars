import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
    APIFY_TOKEN = os.getenv("APIFY_TOKEN", "")
    REDDIT_SUBREDDIT = os.getenv("REDDIT_SUBREDDIT", "ClaudeAI")
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    CREDENTIALS_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "credentials.json"
    )
    TOKEN_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "token.json"
    )

    # Demo credentials — localhost only, never production
    DEMO_USERNAME = "admin"
    DEMO_PASSWORD = "demo123"
