# POST /pay

Accepts a signed Solana transaction that fulfills a prior x402 payment requirement.

### Headers
X-PAYMENT — Base64-encoded payment requirement  
Content-Type — application/json

### Request Body
{
  "serializedTransaction": "Base64EncodedTransaction"
}

### Successful Response (HTTP 200)
{
  "x402Version": 1,
  "settled": true,
  "scheme": "exact",
  "facilitator": "hyperpay",
  "network": "solana",
  "txHash": "TransactionSignature",
  "payTo": "RecipientPublicKey",
  "asset": {
    "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "decimals": 6
  },
  "amount": "10000000",
  "note": "Dinner",
  "timestamp": "2025-10-30T00:00:00Z"
}

### Notes
- Verifies that the transaction transfers the correct amount of USDC.
- Confirms memo match if a note is provided.
- Adds replay protection using transaction hash.
- Returns both a JSON response and a base64 X-PAYMENT-RESPONSE header for clients.
