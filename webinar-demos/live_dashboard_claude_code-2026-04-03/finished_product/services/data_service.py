class DataService:
    """Single responsibility: provide normalized data for dashboard views."""

    def __init__(self, data_repository):
        self._repo = data_repository

    def get_dashboard_data(self):
        normalized = self._repo.get_normalized()
        if normalized is None:
            return {"sheets_data": [], "reddit_data": [], "metadata": None}
        return normalized

    def get_sheets_data(self):
        data = self.get_dashboard_data()
        return data.get("sheets_data", [])

    def get_reddit_data(self):
        data = self.get_dashboard_data()
        return data.get("reddit_data", [])

    def get_metadata(self):
        data = self.get_dashboard_data()
        return data.get("metadata")

    def compute_sheets_metrics(self, sheets_data):
        if not sheets_data:
            return {
                "total_records": 0,
                "total_revenue": 0,
                "avg_revenue": 0,
                "active_count": 0,
            }

        total = len(sheets_data)
        revenues = [r.get("revenue", 0) for r in sheets_data]
        total_revenue = sum(revenues)
        avg_revenue = total_revenue / total if total else 0
        active = sum(1 for r in sheets_data if r.get("status", "").lower() == "active")

        return {
            "total_records": total,
            "total_revenue": total_revenue,
            "avg_revenue": round(avg_revenue, 2),
            "active_count": active,
        }

    def compute_reddit_metrics(self, reddit_data):
        if not reddit_data:
            return {
                "total_posts": 0,
                "avg_score": 0,
                "total_comments": 0,
                "avg_upvote_pct": 0,
                "top_post": None,
            }

        total = len(reddit_data)
        scores = [p.get("score", 0) for p in reddit_data]
        comments = [p.get("comments", 0) for p in reddit_data]
        upvotes = [p.get("upvote_pct", 0) for p in reddit_data]

        sorted_by_score = sorted(reddit_data, key=lambda p: p.get("score", 0), reverse=True)

        return {
            "total_posts": total,
            "avg_score": round(sum(scores) / total, 1) if total else 0,
            "total_comments": sum(comments),
            "avg_upvote_pct": round(sum(upvotes) / total * 100, 1) if total else 0,
            "top_post": sorted_by_score[0] if sorted_by_score else None,
        }

    def get_combined_summary(self):
        data = self.get_dashboard_data()
        sheets = data.get("sheets_data", [])
        reddit = data.get("reddit_data", [])
        return {
            "sheets_metrics": self.compute_sheets_metrics(sheets),
            "reddit_metrics": self.compute_reddit_metrics(reddit),
            "metadata": data.get("metadata"),
        }
