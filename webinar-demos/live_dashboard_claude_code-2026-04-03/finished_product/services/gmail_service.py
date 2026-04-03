"""Send emails via the Gmail API using gmail.send scope."""

import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from google_auth import get_credentials


class GmailService:

    def _service(self):
        creds = get_credentials()
        return build("gmail", "v1", credentials=creds)

    def send_email(self, to, subject, body):
        """Send a plain-text email. Returns the sent message ID."""
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_body = {"raw": raw}

        result = (
            self._service()
            .users()
            .messages()
            .send(userId="me", body=send_body)
            .execute()
        )
        return result.get("id")
