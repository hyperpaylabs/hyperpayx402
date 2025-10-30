# GET /pay

Returns a 402 Payment Required response containing an x402 payment requirement.

### Query Parameters
recipient - Solana wallet address of the recipient  
amount - Payment amount in USDC  
note - Optional memo or payment note

### Response Example (HTTP 402)
{
  "x402Version": 1,
  "accepts": [
    {
      "scheme": "exact",
      "network": "solana",
      "payTo": "RecipientPublicKey",
      "asset": {
        "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "decimals": 6
      },
      "amount": "10000000",
      "note": "Dinner"
    }
  ],
  "facilitator": "hyperpay"
}

### Notes
- Responds with HTTP 402 instead of 200 to signal payment required.
- Used to initiate x402-compliant payments.
