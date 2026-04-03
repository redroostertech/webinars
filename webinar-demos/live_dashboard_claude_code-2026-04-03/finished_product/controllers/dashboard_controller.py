from flask import render_template


class DashboardController:
    """Handles HTTP concerns for dashboard pages. Delegates data to DataService."""

    def __init__(self, data_service):
        self._data = data_service

    def dashboard_page(self):
        all_data = self._data.get_dashboard_data()
        sheets = all_data.get("sheets_data", [])
        reddit = all_data.get("reddit_data", [])
        metadata = all_data.get("metadata")

        sheets_metrics = self._data.compute_sheets_metrics(sheets)
        reddit_metrics = self._data.compute_reddit_metrics(reddit)

        return render_template(
            "dashboard.html",
            sheets_data=sheets,
            reddit_data=reddit[:10],
            sheets_metrics=sheets_metrics,
            reddit_metrics=reddit_metrics,
            metadata=metadata,
        )

    def reddit_page(self):
        reddit = self._data.get_reddit_data()
        metrics = self._data.compute_reddit_metrics(reddit)

        return render_template(
            "reddit.html",
            reddit_data=reddit,
            metrics=metrics,
            metadata=self._data.get_metadata(),
        )

    def summary_page(self):
        summary = self._data.get_combined_summary()

        return render_template(
            "combined.html",
            sheets_metrics=summary["sheets_metrics"],
            reddit_metrics=summary["reddit_metrics"],
            metadata=summary["metadata"],
        )
