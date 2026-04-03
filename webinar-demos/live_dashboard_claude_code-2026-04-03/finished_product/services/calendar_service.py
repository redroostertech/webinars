"""Create Google Calendar events for invoice reminders and follow-ups."""

from googleapiclient.discovery import build

from google_auth import get_credentials


class CalendarService:

    def _service(self):
        creds = get_credentials()
        return build("calendar", "v3", credentials=creds)

    def create_reminder(self, title, date, description=""):
        """Create an all-day Calendar event with 24h popup and email reminders.

        Args:
            title: Event title (e.g. "Invoice INV-0042 due")
            date: Date string in YYYY-MM-DD format
            description: Optional event description

        Returns:
            The event's htmlLink for opening in browser.
        """
        event = {
            "summary": title,
            "description": description,
            "start": {"date": date},
            "end": {"date": date},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 1440},
                    {"method": "email", "minutes": 1440},
                ],
            },
        }

        result = (
            self._service()
            .events()
            .insert(calendarId="primary", body=event)
            .execute()
        )
        return result.get("htmlLink", "")
