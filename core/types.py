# core/types.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class BuiltTx:
    unsigned_b64: str
    recent_blockhash: str
    sender_ata: str
    recipient_ata: str

@dataclass
class PayIntent:
    sender_tg_id: int
    recipient_tg_id: int
    amount_ui: float
    sender_wallet: str
    recipient_wallet: str
    pay_id: Optional[int] = None
