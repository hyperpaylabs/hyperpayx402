export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:4021";

export async function verifyWalletLogin(publicKey: string, signatureBase58: string) {
  const res = await fetch(`${BACKEND_URL}/auth/verify-wallet`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ publicKey, signature: signatureBase58 }),
  });
  if (!res.ok) throw new Error(`Login failed: ${await res.text()}`);
  return res.json() as Promise<{ token: string }>;
}

export async function requestRequirement(recipient: string, amount: string, note?: string) {
  const url = new URL(`${BACKEND_URL}/pay`);
  url.searchParams.set("recipient", recipient);
  url.searchParams.set("amount", amount);
  if (note) url.searchParams.set("note", note);
  const res = await fetch(url.toString());
  if (res.status !== 402) throw new Error(`Unexpected status ${res.status}`);
  return res.json();
}

export async function settlePayment(serializedTransaction: string, requirement: any) {
  const xPayment = btoa(JSON.stringify({ x402Version: 1, ...requirement }));
  const res = await fetch(`${BACKEND_URL}/pay`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-PAYMENT": xPayment,
    },
    body: JSON.stringify({ serializedTransaction }),
  });

  const txt = await res.text();
  const header = res.headers.get("x-payment-response");
  let decoded: any = null;
  if (header) {
    try {
      decoded = JSON.parse(atob(header));
    } catch {
      decoded = null;
    }
  }
  return { ok: res.ok, txt, decoded };
}
