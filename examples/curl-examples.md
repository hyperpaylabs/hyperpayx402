# Example cURL Requests

### Verify Wallet
curl -X POST https://api.hyperpayx402.com/auth/verify-wallet ^
  -H "Content-Type: application/json" ^
  -d "{\"publicKey\":\"<YOUR_PUBLIC_KEY>\",\"signature\":\"<YOUR_SIGNATURE>\"}"

### Get Payment Requirement
curl "https://api.hyperpayx402.com/pay?recipient=<RECIPIENT_PUBLIC_KEY>&amount=10.0&note=Dinner"

### Submit Signed Transaction
curl -X POST https://api.hyperpayx402.com/pay ^
  -H "Content-Type: application/json" ^
  -H "X-PAYMENT: <BASE64_REQUIREMENT>" ^
  -d "{\"serializedTransaction\":\"<BASE64_TRANSACTION>\"}"
