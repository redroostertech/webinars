from flask import jsonify, request


class APIController:
    """Handles HTTP concerns for JSON API endpoints."""

    def __init__(self, data_service, etl_service):
        self._data = data_service
        self._etl = etl_service

    def get_data(self):
        all_data = self._data.get_all_data()
        return jsonify(all_data)

    def sync_data(self):
        """Trigger the full ETL pipeline."""
        results = self._etl.run_full_pipeline()

        if results["errors"]:
            return jsonify({
                "status": "partial" if results["files_processed"] > 0 else "error",
                "message": "; ".join(results["errors"]),
                "files_processed": results["files_processed"],
                "records_added": results["records_added"],
                "timestamp": results["timestamp"],
            }), 200 if results["files_processed"] > 0 else 500

        return jsonify({
            "status": "success",
            "message": (
                f"Sync complete. {results['files_processed']} files processed, "
                f"{results['records_added']} records updated."
            ),
            "timestamp": results["timestamp"],
        })

    def update_lead(self, index):
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        result = self._data.update_record("leads", index, data)
        return jsonify(result)

    def update_invoice(self, index):
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        result = self._data.update_record("invoices", index, data)
        return jsonify(result)

    def update_project(self, index):
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        result = self._data.update_record("projects", index, data)
        return jsonify(result)
