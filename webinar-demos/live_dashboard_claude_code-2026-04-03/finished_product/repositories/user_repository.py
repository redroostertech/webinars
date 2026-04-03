from models.user import User


class UserRepository:
    """Single responsibility: look up users from the backing store."""

    def __init__(self, demo_username, demo_password):
        # For the demo, one hardcoded user. Swap this for a DB query in production.
        self._users = {
            "1": {"username": demo_username, "password": demo_password}
        }

    def find_by_id(self, user_id):
        record = self._users.get(str(user_id))
        if record is None:
            return None
        return User(user_id=user_id, username=record["username"])

    def find_by_credentials(self, username, password):
        for user_id, record in self._users.items():
            if record["username"] == username and record["password"] == password:
                return User(user_id=user_id, username=record["username"])
        return None
