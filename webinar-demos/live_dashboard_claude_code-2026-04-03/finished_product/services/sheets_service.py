import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


class SheetsService:
    """Single responsibility: extract data from Google Sheets API."""

    def __init__(self, credentials_path, token_path):
        self._credentials_path = credentials_path
        self._token_path = token_path

    def _get_credentials(self):
        creds = None

        if os.path.exists(self._token_path):
            creds = Credentials.from_authorized_user_file(self._token_path, SCOPES)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif not creds or not creds.valid:
            if not os.path.exists(self._credentials_path):
                raise FileNotFoundError(
                    f"credentials.json not found at {self._credentials_path}. "
                    "Download it from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                self._credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(self._token_path, "w") as token_file:
            token_file.write(creds.to_json())

        return creds

    def fetch(self, spreadsheet_id, range_name="Sheet1!A1:Z1000"):
        creds = self._get_credentials()
        service = build("sheets", "v4", credentials=creds)
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )

        values = result.get("values", [])
        if not values:
            return {"headers": [], "rows": []}

        headers = values[0]
        rows = values[1:]
        return {"headers": headers, "rows": rows}
