"""Shared Google OAuth helper. All Google services use this to get credentials."""

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import config


def get_credentials():
    """Return authenticated Google credentials, refreshing or prompting as needed."""
    creds = None

    if os.path.exists(config.TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(config.TOKEN_PATH, config.SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(config.CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"Missing {config.CREDENTIALS_PATH}. "
                    "Download it from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                config.CREDENTIALS_PATH, config.SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(config.TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    return creds
