from apify_client import ApifyClient


ACTOR_ID = "trudax/reddit-scraper"


class RedditService:
    """Single responsibility: extract Reddit data via Apify."""

    def __init__(self, apify_token):
        self._token = apify_token

    def fetch(self, subreddit, max_items=25):
        if not self._token:
            raise ValueError(
                "APIFY_TOKEN is not set. Add it to your .env file."
            )

        client = ApifyClient(self._token)

        run_input = {
            "startUrls": [
                {"url": f"https://www.reddit.com/r/{subreddit}/hot"}
            ],
            "maxItems": max_items,
            "proxy": {"useApifyProxy": True},
        }

        run = client.actor(ACTOR_ID).call(run_input=run_input)
        items = list(
            client.dataset(run["defaultDatasetId"]).iterate_items()
        )
        return items
