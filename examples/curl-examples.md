# Example cURL Requests (Localhost)

### Verify Wallet (optional; requires Firebase configured locally)
curl -X POST http://localhost:4021/auth/verify-wallet ^
  -H "Content-Type: application/json" ^
  -d "{\"publicKey\":\"<YOUR_PUBLIC_KEY>\",\"signature\":\"<YOUR_SIGNATURE>\"}"

### Get Payment Requirement
curl "http://localhost:4021/pay?recipient=<RECIPIENT_PUBLIC_KEY>&amount=10.0&note=Dinner"

### Submit Signed Transaction
curl -X POST http://localhost:4021/pay ^
  -H "Content-Type: application/json" ^
  -H "X-PAYMENT: <BASE64_REQUIREMENT>" ^
  -d "{\"serializedTransaction\":\"<BASE64_TRANSACTION>\"}"
