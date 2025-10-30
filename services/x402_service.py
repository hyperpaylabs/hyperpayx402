# services/x402_service.py
from core.db import DB

class X402Service:
    def __init__(self, db: DB):
        self.db = db

    def create_invoice(self, resource_id: str, price_usdc_int: int, buyer_tg_id: int | None = None) -> int:
        self.db.execute(
            "INSERT INTO invoices(resource_id, buyer_tg_id, price_usdc, status) VALUES (?,?,?,?)",
            (resource_id, buyer_tg_id, price_usdc_int, "OPEN")
        )
        return self.db.last_row_id

    def mark_paid(self, invoice_id: int):
        self.db.execute("UPDATE invoices SET status='PAID' WHERE id=?", (invoice_id,))

    def get_invoice(self, invoice_id: int):
        return self.db.fetch_one("SELECT * FROM invoices WHERE id=?", (invoice_id,))
