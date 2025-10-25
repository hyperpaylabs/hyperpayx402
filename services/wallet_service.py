# services/wallet_service.py
from typing import Optional
from core.db import DB

class WalletService:
    def __init__(self, db: DB):
        self.db = db

    def add_wallet(self, tg_user_id: int, username: str | None, pubkey: str, make_active=True):
        self.db.execute("INSERT OR IGNORE INTO users(tg_user_id, username) VALUES (?, ?)", (tg_user_id, username))
        if username:
            self.db.execute("UPDATE users SET username=? WHERE tg_user_id=?", (username, tg_user_id))
        if make_active:
            self.db.execute("UPDATE wallets SET is_active=0 WHERE tg_user_id=?", (tg_user_id,))
        self.db.execute(
            "INSERT OR IGNORE INTO wallets(tg_user_id, label, pubkey, is_active) VALUES (?,?,?,?)",
            (tg_user_id, "Phantom", pubkey, 1 if make_active else 0)
        )

    def list_wallets(self, tg_user_id: int):
        return self.db.fetch_all("SELECT pubkey, is_active FROM wallets WHERE tg_user_id=?", (tg_user_id,))

    def set_active(self, tg_user_id: int, pubkey: str):
        self.db.execute("UPDATE wallets SET is_active=0 WHERE tg_user_id=?", (tg_user_id,))
        self.db.execute("UPDATE wallets SET is_active=1 WHERE tg_user_id=? AND pubkey=?", (tg_user_id, pubkey))

    def disconnect(self, tg_user_id: int, pubkey: str):
        self.db.execute("DELETE FROM wallets WHERE tg_user_id=? AND pubkey=?", (tg_user_id, pubkey))

    def active_wallet(self, tg_user_id: int) -> Optional[str]:
        row = self.db.fetch_one("SELECT pubkey FROM wallets WHERE tg_user_id=? AND is_active=1", (tg_user_id,))
        return row["pubkey"] if row else None
