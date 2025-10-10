# services/rpc.py
import requests
from typing import Any, Dict, Optional

class Rpc:
    def __init__(self, url: str):
        self.url = url

    def _raw(self, method: str, params: Any) -> Dict:
        r = requests.post(
            self.url,
            json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
            timeout=25,
        )
        r.raise_for_status()
        return r.json()

    def call(self, method: str, params: Any) -> Dict:
        j = self._raw(method, params)
        if "error" in j:
            err = j["error"]
            msg = err.get("message", str(err))
            raise RuntimeError(f"RPC error in {method}: {msg}")
        return j["result"]

    def get_latest_blockhash(self) -> str:
        res = self.call("getLatestBlockhash", [{"commitment": "finalized"}])
        return res["value"]["blockhash"]

    def get_account_info(self, pubkey: str) -> Optional[Dict]:
        try:
            j = self._raw("getAccountInfo", [pubkey, {"encoding": "base64"}])
            if "error" in j:
                return None
            return j.get("result", {}).get("value")
        except Exception:
            return None

    def get_balance_lamports(self, pubkey: str) -> int:
        res = self.call("getBalance", [pubkey, {"commitment": "processed"}])
        return int(res["value"])

    def get_token_account_by_owner(self, owner: str, mint: str) -> Optional[str]:
        """Return first token account address for (owner, mint) if any."""
        res = self.call("getTokenAccountsByOwner", [owner, {"mint": mint}, {"encoding": "jsonParsed"}])
        arr = res.get("value", [])
        if not arr:
            return None
        return arr[0]["pubkey"]

    def get_token_balance_ui(self, token_account: str) -> float:
        res = self.call("getTokenAccountBalance", [token_account, {"commitment": "processed"}])
        v = res["value"]
        # uiAmountString is accurate and avoids float rounding
        return float(v.get("uiAmount", v.get("uiAmountString", "0")))

    def send_raw_transaction(self, raw_base64: str) -> str:
        # IMPORTANT: base64
        res = self.call(
            "sendTransaction",
            [raw_base64, {"encoding": "base64", "skipPreflight": False, "maxRetries": 3}],
        )
        return res
