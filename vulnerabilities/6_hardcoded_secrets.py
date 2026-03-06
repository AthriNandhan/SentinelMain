import json

def process_payment(request_payload):
    """
    VULNERABILITY: Hardcoded Secrets
    Demonstrates storing sensitive API keys directly in the source code.
    """
    try:
        data = json.loads(request_payload)
        amount = data.get("amount", 0)
        
        # VULNERABLE: Hardcoded Stripe API key
        #STRIPE_API_KEY = "sk_live_1234567890abcdef12345678"
        
        if amount <= 0:
             return {"status": "error", "message": "Invalid amount"}
             
        # Mock payment processing
        print(f"Processing ${amount} using key starting with {STRIPE_API_KEY[:7]}...")
        
        # Simulating that exploiting this involves finding the code which has the key.
        # We return the flag here just so test_harness can verify the exploit structure.
        return {"status": "success", "data": "Payment processed successfully. Leaked: SECRET_FLAG_DATA_123"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
