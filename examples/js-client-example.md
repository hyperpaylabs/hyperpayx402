# Example JavaScript Client (Node.js, Localhost)

import fetch from "node-fetch";

const BASE_URL = "http://localhost:4021";

export async function verifyWallet(publicKey, signature) {
  const res = await fetch(`${BASE_URL}/auth/verify-wallet`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ publicKey, signature }),
  });
  return await res.json();
}

export async function getPayment(recipient, amount, note) {
  const url = new URL(`${BASE_URL}/pay`);
  url.searchParams.set("recipient", recipient);
  url.searchParams.set("amount", String(amount));
  if (note) url.searchParams.set("note", note);

  const res = await fetch(url.toString());
  if (res.status === 402) {
    return await res.json();
  }
  throw new Error(`Unexpected response status: ${res.status}`);
}

export async function submitSignedTransaction(base64Requirement, base64Tx) {
  const res = await fetch(`${BASE_URL}/pay`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-PAYMENT": base64Requirement,
    },
    body: JSON.stringify({ serializedTransaction: base64Tx }),
  });
  const body = await res.json();
  const header = res.headers.get("x-payment-response"); // base64 of the same JSON
  return { body, header };
}

/**
 * Notes
 * - BASE_URL points to your local TypeScript server (http://localhost:4021).
 * - `getPayment()` returns the x402-style requirement when HTTP 402 is received.
 * - `submitSignedTransaction()` must include `X-PAYMENT` (base64 requirement) and your base64 serialized transaction.
 */
