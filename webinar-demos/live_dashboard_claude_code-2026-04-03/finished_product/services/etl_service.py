"""Orchestrate the full ETL pipeline: Drive -> normalize -> reconcile -> Sheets."""

import json
import os
from datetime import datetime, timezone

import config


class ETLService:

    def __init__(self, drive_service, sheets_service, openai_service):
        self._drive = drive_service
        self._sheets = sheets_service
        self._openai = openai_service
        self._state_path = os.path.join(config.DATA_DIR, "sync_state.json")
        os.makedirs(config.DATA_DIR, exist_ok=True)

    def _load_state(self):
        if os.path.exists(self._state_path):
            with open(self._state_path, "r") as f:
                return json.load(f)
        return {}

    def _save_state(self, state):
        with open(self._state_path, "w") as f:
            json.dump(state, f, indent=2, default=str)

    def run_full_pipeline(self):
        """Run the complete ETL pipeline. Handles partial failures gracefully."""
        state = self._load_state()
        last_sync = state.get("last_sync_times", {})
        errors = []
        files_processed = 0
        records_added = 0

        # Step 1: Scan Drive folders
        try:
            new_files = self._drive.scan_all_folders(last_sync)
        except Exception as e:
            return {
                "status": "error",
                "errors": [f"Drive scan failed: {str(e)}"],
                "files_processed": 0,
                "records_added": 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # Step 2: Read existing data from Sheets
        existing = {"leads": [], "invoices": [], "projects": []}
        for tab_name in existing:
            try:
                headers, rows = self._sheets.read_tab(tab_name.capitalize())
                for row in rows:
                    record = {}
                    for i, h in enumerate(headers):
                        record[h] = row[i] if i < len(row) else ""
                    existing[tab_name].append(record)
            except Exception:
                pass

        # Step 3: Read and normalize each new file
        all_new_data = {"leads": [], "invoices": [], "projects": []}
        for object_type, files in new_files.items():
            for file_info in files:
                try:
                    headers, rows = self._drive.read_spreadsheet(file_info["id"])
                    if not headers or not rows:
                        continue
                    normalized = self._openai.normalize(headers, rows, object_type)
                    all_new_data[object_type].extend(normalized)
                    files_processed += 1
                except Exception as e:
                    errors.append(
                        f"Failed to process {file_info['name']}: {str(e)}"
                    )

        # Step 4: Reconcile if we have new data
        total_new = sum(len(v) for v in all_new_data.values())
        if total_new > 0:
            try:
                reconciled = self._openai.reconcile(
                    all_new_data,
                    existing["leads"],
                    existing["invoices"],
                    existing["projects"],
                )
            except Exception as e:
                errors.append(f"Reconciliation failed: {str(e)}")
                reconciled = {
                    "leads": existing["leads"] + all_new_data["leads"],
                    "invoices": existing["invoices"] + all_new_data["invoices"],
                    "projects": existing["projects"] + all_new_data["projects"],
                }

            # Step 5: Write reconciled data back to Sheets
            for tab_name, records in reconciled.items():
                if not records:
                    continue
                try:
                    headers = list(records[0].keys())
                    rows = [headers]
                    for record in records:
                        rows.append([str(record.get(h, "")) for h in headers])
                    self._sheets.write_tab(tab_name.capitalize(), rows)
                    records_added += len(records)
                except Exception as e:
                    errors.append(f"Failed to write {tab_name}: {str(e)}")

        # Step 6: Update sync state
        now = datetime.now(timezone.utc).isoformat()
        for object_type, files in new_files.items():
            if files:
                last_sync[object_type] = max(f["modifiedTime"] for f in files)

        state["last_sync_times"] = last_sync
        state["last_run"] = now
        state["last_result"] = {
            "files_processed": files_processed,
            "records_added": records_added,
            "errors": errors,
        }
        self._save_state(state)

        return {
            "status": "error" if errors else "success",
            "errors": errors,
            "files_processed": files_processed,
            "records_added": records_added,
            "timestamp": now,
        }

    def get_last_sync_info(self):
        """Return info about the last pipeline run."""
        state = self._load_state()
        return {
            "last_run": state.get("last_run"),
            "last_result": state.get("last_result"),
        }
