"""Scan Google Drive folders for new or updated spreadsheets."""

from googleapiclient.discovery import build

import config
from google_auth import get_credentials


class DriveService:

    FOLDER_MAP = {
        "leads": config.DRIVE_LEADS_FOLDER,
        "invoices": config.DRIVE_INVOICES_FOLDER,
        "projects": config.DRIVE_PROJECTS_FOLDER,
    }

    def _service(self):
        creds = get_credentials()
        return build("drive", "v3", credentials=creds)

    def list_spreadsheets(self, folder_id):
        """Return list of Google Spreadsheets in a folder with id, name, modifiedTime."""
        query = (
            f"'{folder_id}' in parents "
            "and mimeType='application/vnd.google-apps.spreadsheet' "
            "and trashed=false"
        )
        results = (
            self._service()
            .files()
            .list(q=query, fields="files(id, name, modifiedTime)", orderBy="modifiedTime desc")
            .execute()
        )
        return results.get("files", [])

    def scan_all_folders(self, last_sync_times=None):
        """Scan all three Drive folders and return files newer than last sync.

        Returns dict: {"leads": [...], "invoices": [...], "projects": [...]}
        Each item has keys: id, name, modifiedTime, object_type
        """
        if last_sync_times is None:
            last_sync_times = {}

        new_files = {}
        for object_type, folder_id in self.FOLDER_MAP.items():
            if not folder_id:
                new_files[object_type] = []
                continue

            all_files = self.list_spreadsheets(folder_id)
            cutoff = last_sync_times.get(object_type)

            if cutoff:
                files = [f for f in all_files if f["modifiedTime"] > cutoff]
            else:
                files = all_files

            for f in files:
                f["object_type"] = object_type

            new_files[object_type] = files

        return new_files

    def read_spreadsheet(self, file_id):
        """Read all values from the first sheet of a Google Spreadsheet.

        Returns (headers, rows) where headers is a list of strings
        and rows is a list of lists.
        """
        creds = get_credentials()
        sheets_svc = build("sheets", "v4", credentials=creds)
        result = (
            sheets_svc.spreadsheets()
            .values()
            .get(spreadsheetId=file_id, range="Sheet1")
            .execute()
        )
        values = result.get("values", [])
        if len(values) < 1:
            return [], []
        return values[0], values[1:]
