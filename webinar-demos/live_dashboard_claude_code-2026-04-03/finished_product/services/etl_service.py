from datetime import datetime, timezone


class ETLService:
    """Single responsibility: orchestrate the full Extract-Transform-Load pipeline."""

    def __init__(self, sheets_service, reddit_service, data_repository, config):
        self._sheets = sheets_service
        self._reddit = reddit_service
        self._repo = data_repository
        self._config = config

    def extract_sheets(self):
        raw = self._sheets.fetch(self._config.GOOGLE_SHEET_ID)
        self._repo.save_sheets_raw(raw)
        return len(raw.get("rows", []))

    def extract_reddit(self):
        posts = self._reddit.fetch(
            self._config.REDDIT_SUBREDDIT,
            max_items=25,
        )
        self._repo.save_reddit_raw(posts)
        return len(posts)

    def normalize(self):
        sheets_raw = self._repo.get_sheets_raw()
        reddit_raw = self._repo.get_reddit_raw()

        sheets_data = self._normalize_sheets(sheets_raw)
        reddit_data = self._normalize_reddit(reddit_raw)

        self._repo.save_normalized(sheets_data, reddit_data)
        return len(sheets_data), len(reddit_data)

    def run_full_pipeline(self):
        results = {"sheets_rows": 0, "reddit_posts": 0, "errors": []}

        try:
            results["sheets_rows"] = self.extract_sheets()
        except Exception as e:
            results["errors"].append(f"Sheets fetch failed: {e}")

        try:
            results["reddit_posts"] = self.extract_reddit()
        except Exception as e:
            results["errors"].append(f"Reddit fetch failed: {e}")

        try:
            self.normalize()
        except Exception as e:
            results["errors"].append(f"Normalization failed: {e}")

        results["timestamp"] = datetime.now(timezone.utc).isoformat()
        return results

    def _normalize_sheets(self, raw):
        if raw is None:
            return []

        headers = [h.lower().strip() for h in raw.get("headers", [])]
        rows = raw.get("rows", [])
        normalized = []

        for row in rows:
            record = {}
            for i, header in enumerate(headers):
                value = row[i] if i < len(row) else ""
                record[header] = value
            # Cast numeric fields
            if "revenue" in record:
                try:
                    record["revenue"] = float(record["revenue"])
                except (ValueError, TypeError):
                    record["revenue"] = 0
            normalized.append(record)

        return normalized

    def _normalize_reddit(self, raw):
        if raw is None:
            return []

        # Field mapping: Apify field name -> our schema name
        field_map = {
            "title": "title",
            "score": "score",
            "numberOfComments": "comments",
            "upvoteRatio": "upvote_pct",
            "author": "author",
            "subreddit": "subreddit",
            "createdAt": "posted_at",
            "url": "url",
        }

        normalized = []
        for post in raw:
            record = {}
            for apify_key, our_key in field_map.items():
                record[our_key] = post.get(apify_key, "" if our_key in ("title", "author", "subreddit", "url", "posted_at") else 0)
            normalized.append(record)

        return sorted(normalized, key=lambda p: p.get("score", 0), reverse=True)
