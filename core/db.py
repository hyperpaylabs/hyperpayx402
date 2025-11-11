# core/db.py
import sqlite3
import threading

class DB:
    def __init__(self, filename: str):
        self.filename = filename
        self.lock = threading.Lock()
        self._last_row_id = None
        self._ensure_tables()
        self._migrate_schema()

    # ---------- Base helpers ----------
    def _get_conn(self):
        conn = sqlite3.connect(self.filename, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def execute(self, query: str, params: tuple = ()):
        """Execute a write and return cursor.lastrowid (None for non-INSERTs)."""
        with self.lock:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            rid = cur.lastrowid
            conn.close()
            self._last_row_id = rid
            return rid

    def fetch_one(self, query: str, params: tuple = ()):
        with self.lock:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute(query, params)
            row = cur.fetchone()
            conn.close()
            return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple = ()):
        with self.lock:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()
            conn.close()
            return [dict(r) for r in rows]

    # Back-compat if some code still calls these:
    def last_id(self):
        return self._last_row_id
    def last_row_id(self):  # alias
        return self._last_row_id

    # ---------- Schema ----------
    def _ensure_tables(self):
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()

            c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_user_id INTEGER UNIQUE,
                username TEXT,
                created_ts REAL DEFAULT (strftime('%s','now'))
            )
            """)

            c.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_user_id INTEGER,
                wallet_address TEXT,
                private_key TEXT,
                is_active INTEGER DEFAULT 0,
                created_ts REAL DEFAULT (strftime('%s','now'))
            )
            """)

            c.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_tg_id INTEGER,
                sender_wallet TEXT,
                recipient_tg_id INTEGER,
                recipient_wallet TEXT,
                amount_usdc INTEGER,
                status TEXT DEFAULT 'PENDING',
                tx_signature TEXT,
                created_ts REAL DEFAULT (strftime('%s','now'))
            )
            """)

            c.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER,
                recip_id INTEGER,
                ts REAL,
                payment_id INTEGER,
                fulfilled INTEGER DEFAULT 0
            )
            """)

            conn.commit()
            conn.close()

    # ---------- Migrations ----------
    def _table_info(self, table: str):
        with self.lock:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute(f"PRAGMA table_info({table})")
            rows = cur.fetchall()
            conn.close()
            return [dict(r) for r in rows]

    def _has_column(self, table: str, column: str) -> bool:
        return any(col["name"] == column for col in self._table_info(table))

    def _migrate_schema(self):
        # wallets.wallet_address (backfill from legacy names)
        if not self._has_column("wallets", "wallet_address"):
            self.execute("ALTER TABLE wallets ADD COLUMN wallet_address TEXT")
            if self._has_column("wallets", "address"):
                self.execute("UPDATE wallets SET wallet_address=address WHERE wallet_address IS NULL")
            elif self._has_column("wallets", "pubkey"):
                self.execute("UPDATE wallets SET wallet_address=pubkey WHERE wallet_address IS NULL")

        # requests.payment_id
        if not self._has_column("requests", "payment_id"):
            self.execute("ALTER TABLE requests ADD COLUMN payment_id INTEGER")

        # requests.fulfilled
        if not self._has_column("requests", "fulfilled"):
            self.execute("ALTER TABLE requests ADD COLUMN fulfilled INTEGER DEFAULT 0")

    # ---------- User management ----------
    def ensure_user(self, tg_user_id: int, username: str | None):
        row = self.fetch_one("SELECT * FROM users WHERE tg_user_id=?", (tg_user_id,))
        if not row:
            self.execute("INSERT INTO users (tg_user_id, username) VALUES (?, ?)", (tg_user_id, username))
        elif username and row["username"] != username:
            self.execute("UPDATE users SET username=? WHERE tg_user_id=?", (username, tg_user_id))

    def get_user_by_username(self, username: str):
        return self.fetch_one("SELECT * FROM users WHERE LOWER(username)=?", (username.lower(),))

    def get_user_by_id(self, tg_user_id: int):
        return self.fetch_one("SELECT * FROM users WHERE tg_user_id=?", (tg_user_id,))

    # ---------- Wallet management ----------
    def add_wallet(self, tg_user_id: int, wallet_address: str, private_key: str):
        return self.execute(
            "INSERT INTO wallets (tg_user_id, wallet_address, private_key) VALUES (?, ?, ?)",
            (tg_user_id, wallet_address, private_key),
        )

    def set_active_wallet(self, tg_user_id: int, wallet_address: str):
        self.execute("UPDATE wallets SET is_active=0 WHERE tg_user_id=?", (tg_user_id,))
        self.execute(
            "UPDATE wallets SET is_active=1 WHERE tg_user_id=? AND wallet_address=?",
            (tg_user_id, wallet_address),
        )

    def get_active_wallet(self, tg_user_id: int):
        return self.fetch_one("SELECT * FROM wallets WHERE tg_user_id=? AND is_active=1", (tg_user_id,))

    def list_wallets(self, tg_user_id: int):
        return self.fetch_all("SELECT * FROM wallets WHERE tg_user_id=?", (tg_user_id,))

    # ---------- Payments ----------
    def add_payment(self, sender_tg_id, sender_wallet, recip_tg_id, recip_wallet, amount_usdc, status="PENDING"):
        return self.execute(
            "INSERT INTO payments (sender_tg_id, sender_wallet, recipient_tg_id, recipient_wallet, amount_usdc, status) "
            "VALUES (?,?,?,?,?,?)",
            (sender_tg_id, sender_wallet, recip_tg_id, recip_wallet, amount_usdc, status),
        )

    def update_payment_status(self, payment_id, status, tx_sig=None):
        self.execute("UPDATE payments SET status=?, tx_signature=? WHERE id=?", (status, tx_sig, payment_id))

    def get_payment(self, payment_id):
        return self.fetch_one("SELECT * FROM payments WHERE id=?", (payment_id,))

    # ---------- Requests ----------
    def add_request(self, sender_id: int, recip_id: int, ts: float, payment_id: int | None = None):
        return self.execute(
            "INSERT INTO requests (sender_id, recip_id, ts, payment_id, fulfilled) VALUES (?,?,?,?,0)",
            (sender_id, recip_id, ts, payment_id),
        )

    def mark_request_fulfilled(self, request_id: int, payment_id: int):
        self.execute("UPDATE requests SET fulfilled=1, payment_id=? WHERE id=?", (payment_id, request_id))

    def find_latest_unfulfilled_request(self, requester_id: int, payer_id: int):
        return self.fetch_one(
            "SELECT * FROM requests WHERE sender_id=? AND recip_id=? AND (fulfilled IS NULL OR fulfilled=0) "
            "ORDER BY ts DESC LIMIT 1",
            (requester_id, payer_id),
        )

    def get_recent_requests(self, sender_id, recip_id):
        return self.fetch_all(
            "SELECT * FROM requests WHERE sender_id=? AND recip_id=? ORDER BY ts DESC LIMIT 5",
            (sender_id, recip_id),
        )
