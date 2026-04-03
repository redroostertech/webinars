class AuthService:
    """Single responsibility: authenticate users."""

    def __init__(self, user_repository):
        self._user_repo = user_repository

    def login(self, username, password):
        return self._user_repo.find_by_credentials(username, password)

    def load_user(self, user_id):
        return self._user_repo.find_by_id(user_id)
