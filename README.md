# Hyper Pay x402 - TypeScript API & Local Server Setup

Hyper Pay x402 is a web-native payment layer that brings peer-to-peer payments to Solana using the x402 open protocol.

This repository includes:
- Complete Express + TypeScript backend implementation
- API documentation for x402-compliant payment handling
- Local setup instructions (Node, TypeScript, Firebase optional)
- Example requests and integration guidance

---

## Overview

- Base URL: `https://api.hyperpayx402.com` (production)  
- Local Dev URL: `http://localhost:4021`
- Network: Solana Mainnet  
- Asset: USDC (EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v)  
- Protocol: x402 v1  
- Language: TypeScript

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

If Firebase credentials are not configured, the server will respond:
```json
{ "error": "Not Implemented" }
```

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

**Headers**
- X-PAYMENT: base64-encoded x402 payment requirement

**Body Example**
```json
{ "serializedTransaction": "Base64EncodedTransaction" }
```

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

# Local Development Setup (Hands-Free Guide)

This backend runs entirely locally using TypeScript + Node.js.

## 1. Install Node.js
Download and install the LTS version from https://nodejs.org/en/download

Verify install:
```bash
node -v
npm -v
```

## 2. Clone the Repository
```bash
git clone https://github.com/hyperpaylabs/hyperpayx402.git
cd hyperpayx402
```

## 3. Setup the Backend
```bash
cd server
```

### Create .env
```bash
copy .env.example .env
```
Then edit .env and add your own RPC if needed.

### Example .env
```
RPC_URL=https://mainnet.helius-rpc.com/?api-key=YOUR_KEY
PORT=4021
USDC_MINT=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
USDC_DECIMALS=6
```

### Install Dependencies
```bash
npm install
```

### Compile TypeScript
```bash
npx tsc
```

### Run the Server
```bash
npx ts-node index.ts
# or
npm run start
```

The API will now be available at:
```
http://localhost:4021
```

---

## Firebase Setup (Optional)
If you want to enable `/auth/verify-wallet`, add Firebase Admin:

1. Create a Firebase project and go to Project Settings > Service Accounts  
2. Click Generate new private key and download the JSON.  
3. Place it in /server/serviceAccount.json  

If Firebase is not configured, `/auth/verify-wallet` will still respond safely with `{ error: "Not Implemented" }`.

---

## Test Locally with cURL

```bash
# Verify Wallet (Firebase enabled)
curl -X POST http://localhost:4021/auth/verify-wallet   -H "Content-Type: application/json"   -d "{"publicKey":"<BASE58_PUBKEY>","signature":"<BASE58_SIG>"}"

# Get Payment Requirement
curl "http://localhost:4021/pay?recipient=<RECIPIENT>&amount=10.0&note=Dinner" -i

# Submit Signed Transaction
curl -X POST http://localhost:4021/pay   -H "Content-Type: application/json"   -H "X-PAYMENT: <BASE64_REQUIREMENT>"   -d "{"serializedTransaction":"<BASE64_TX>"}" -i
```

---

## Repository Structure

```
hyperpayx402/
|-- endpoints/             # Markdown endpoint documentation
|-- examples/              # Example cURL + JS client usage
|-- server/                # Backend TypeScript source
|   |-- index.ts
|   |-- package.json
|   |-- tsconfig.json
|   |-- .env.example
|   `-- serviceAccount.json  (optional, not committed)
|-- README.md
```

---

## Licensing

These docs and backend are open-sourced for integration and educational purposes.  
You may clone, modify, and run locally, but commercial redistribution is prohibited without consent.

License: MIT

---

## Contact

For integration inquiries or technical questions, contact the Hyper Pay x402 Development Team via X (Twitter).

