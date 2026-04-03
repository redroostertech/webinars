from flask import jsonify


class APIController:
    """Handles HTTP concerns for JSON API endpoints."""

    def __init__(self, data_service, etl_service):
        self._data = data_service
        self._etl = etl_service

    def get_data(self):
        all_data = self._data.get_dashboard_data()
        return jsonify(all_data)

    def refresh_data(self):
        results = self._etl.run_full_pipeline()

        if results["errors"]:
            return jsonify({
                "status": "error",
                "message": "; ".join(results["errors"]),
                "timestamp": results["timestamp"],
            }), 500

        return jsonify({
            "status": "success",
            "message": (
                f"Data refreshed. {results['sheets_rows']} Sheets rows, "
                f"{results['reddit_posts']} Reddit posts loaded."
            ),
            "timestamp": results["timestamp"],
        })
