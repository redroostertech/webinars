"""Read and write the master Google Spreadsheet (single source of truth)."""

from googleapiclient.discovery import build

import config
from google_auth import get_credentials


class SheetsService:

    def __init__(self):
        self._sheet_id = config.MASTER_SHEET_ID

    def _service(self):
        """Build a fresh Sheets API client each call to avoid stale tokens."""
        creds = get_credentials()
        return build("sheets", "v4", credentials=creds)

    def read_tab(self, tab_name):
        """Return (headers, rows) from a sheet tab. Rows are lists of strings."""
        result = (
            self._service()
            .spreadsheets()
            .values()
            .get(spreadsheetId=self._sheet_id, range=tab_name)
            .execute()
        )
        values = result.get("values", [])
        if len(values) < 1:
            return [], []
        return values[0], values[1:]

    def write_tab(self, tab_name, rows):
        """Overwrite an entire tab with rows (first row = headers)."""
        body = {"values": rows}
        self._service().spreadsheets().values().update(
            spreadsheetId=self._sheet_id,
            range=tab_name,
            valueInputOption="RAW",
            body=body,
        ).execute()

    def append_rows(self, tab_name, rows):
        """Append rows to the bottom of a tab."""
        body = {"values": rows}
        self._service().spreadsheets().values().append(
            spreadsheetId=self._sheet_id,
            range=tab_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()

    def read_tab_from_sheet(self, sheet_id, tab_name):
        """Read from any sheet by ID (not just the master)."""
        result = (
            self._service()
            .spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=tab_name)
            .execute()
        )
        values = result.get("values", [])
        if len(values) < 1:
            return [], []
        return values[0], values[1:]

    def write_tab_to_sheet(self, sheet_id, tab_name, rows):
        """Write to any sheet by ID (not just the master)."""
        body = {"values": rows}
        self._service().spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=tab_name,
            valueInputOption="RAW",
            body=body,
        ).execute()
