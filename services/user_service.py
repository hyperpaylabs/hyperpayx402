# services/user_service.py
from core.db import DB

class UserService:
    def __init__(self, db: DB):
        self.db = db

    def ensure_user(self, tg_user_id: int, username: str | None):
        self.db.execute("INSERT OR IGNORE INTO users(tg_user_id, username) VALUES (?, ?)", (tg_user_id, username))
        if username:
            self.db.execute("UPDATE users SET username=? WHERE tg_user_id=?", (username, tg_user_id))

    def find_by_username_or_id(self, username: str | None, user_id: int | None):
        if username:
            row = self.db.fetch_one("SELECT tg_user_id FROM users WHERE username=?", (username,))
            if row: return row["tg_user_id"]
        if user_id:
            row = self.db.fetch_one("SELECT tg_user_id FROM users WHERE tg_user_id=?", (user_id,))
            if row: return row["tg_user_id"]
        return None
