# services/phantom_link.py
from urllib.parse import urlencode
from core.config import PUBLIC_BASE_URL

class PhantomLink:
    """
    Build a link to our local signing page. The page auto-fetches a fresh unsigned
    tx from /phantom/build?state=... and immediately asks Phantom to sign it.
    """

    def __init__(self):
        self.local_sign_path = "/phantom/sign"

    def build_sign_link(self, _unsigned_b64: str, extra: dict | None = None) -> str:
        """
        We ignore unsigned_b64 in this flow and rely on 'state' to rebuild fresh.
        We add autorun=1 so the page signs immediately (no extra click).
        """
        params = {"autorun": "1"}
        if extra:
            params.update(extra)  # should include {"state": "<payment_id>"}
        return f"{PUBLIC_BASE_URL}{self.local_sign_path}?{urlencode(params)}"
