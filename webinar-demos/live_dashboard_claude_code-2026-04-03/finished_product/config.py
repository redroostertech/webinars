import os

from dotenv import load_dotenv

load_dotenv()

# Flask
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
PORT = 3456

# Demo auth
DEMO_USERNAME = os.getenv("DEMO_USERNAME", "admin")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "demo123")

# Google Sheets — master datastore
MASTER_SHEET_ID = os.getenv("MASTER_SHEET_ID", "")

# Projects sheet — where the project list lives
PROJECTS_SHEET_ID = os.getenv("PROJECTS_SHEET_ID", "")

# Google Drive folder IDs
DRIVE_LEADS_FOLDER = os.getenv("DRIVE_LEADS_FOLDER", "")
DRIVE_INVOICES_FOLDER = os.getenv("DRIVE_INVOICES_FOLDER", "")
DRIVE_PROJECTS_FOLDER = os.getenv("DRIVE_PROJECTS_FOLDER", "")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Google OAuth scopes (one credentials.json for all four services)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.events",
]

# File watcher
DRIVE_SYNC_PATH = os.getenv("DRIVE_SYNC_PATH", "")
WATCH_ENABLED = os.getenv("WATCH_ENABLED", "false").lower() == "true"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SAMPLE_DATA_DIR = os.path.join(DATA_DIR, "sample")
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")
