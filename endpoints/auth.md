# POST /auth/verify-wallet

Verifies ownership of a Solana wallet by checking a signed message.

### Request Body
{
  "publicKey": "Base58PublicKey",
  "signature": "Base58Signature"
}

### Response Example
{
  "token": "FirebaseCustomToken"
}

### Notes
- The signed message must be "Login to Hyper Pay x402".
- Returns a Firebase authentication token for future requests.
- This endpoint prevents impersonation by verifying signatures with TweetNaCl.
