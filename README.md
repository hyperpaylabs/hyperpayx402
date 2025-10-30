# Hyper Pay x402 API Documentation

Hyper Pay x402 is a web-native payment layer that brings peer-to-peer payments to Solana using the x402 open protocol.

This documentation describes the available HTTP endpoints for wallet authentication and x402-compliant payment processing.

> Note: These docs are provided for developers and partners integrating with Hyper Pay x402.  
> The backend implementation and deployment configuration remain private.

---

## Overview

- **Base URL:** `https://api.hyperpayx402.com`
- **Network:** Solana Mainnet
- **Asset:** USDC (Mint: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v)
- **Protocol:** x402 v1

### Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/verify-wallet` | Verifies a signed wallet login message |
| GET | `/pay` | Returns x402 payment requirement (HTTP 402 response) |
| POST | `/pay` | Accepts signed Solana transaction and settles payment |

---

## Authentication

All interactions start by verifying a wallet signature using `/auth/verify-wallet`.

Clients must sign the fixed message `Login to Hyper Pay x402` with their Solana wallet and send:

```json
{
  "publicKey": "Base58PublicKey",
  "signature": "Base58Signature"
}
```

Successful verification returns a Firebase Auth token for subsequent requests.

---

## Example: GET /pay

Returns a 402 Payment Required response containing an x402 payment requirement.

**Query Parameters**  
- `recipient`: Solana public key of the recipient  
- `amount`: Payment amount in USDC  
- `note`: Optional memo attached to the payment

**Response Example (HTTP 402)**

```json
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
```

---

## Example: POST /pay

Accepts a signed Solana transaction and finalizes payment.

**Body Example**

```json
{
  "serializedTransaction": "Base64EncodedTransaction"
}
```

**Headers**
- `X-PAYMENT`: base64-encoded x402 payment requirement

**Success Response**

```json
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
```

---

## Licensing

These docs are provided under a limited integration license.  
You may use them for testing or integration but may not redistribute or deploy backend logic.

---

## Contact

For integration inquiries or technical questions, contact the Hyper Pay x402 development team on X.
