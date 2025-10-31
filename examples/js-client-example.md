# Example JavaScript Client (Node.js)

import fetch from "node-fetch";

const BASE_URL = "coming soon";

async function verifyWallet(publicKey, signature) {
  const res = await fetch(`${BASE_URL}/auth/verify-wallet`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ publicKey, signature }),
  });
  return await res.json();
}

async function getPayment(recipient, amount, note) {
  const res = await fetch(`${BASE_URL}/pay?recipient=${recipient}&amount=${amount}&note=${note}`);
  if (res.status === 402) return await res.json();
  throw new Error("Unexpected response");
}

### Notes
- Replace BASE_URL with your test or production endpoint.
- Attach the base64 payment header when posting the signed transaction for full x402 compliance.
