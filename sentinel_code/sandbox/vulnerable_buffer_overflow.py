import json

def process_input(request_payload):
    """Simulates unsafe buffer handling that may raise an overflow error."""
    data = json.loads(request_payload)
    user_input = data.get("input", "")
    
    # Vulnerable: writes directly into fixed-size bytearray
    buf = bytearray(10)
    try:
        for i, ch in enumerate(user_input.encode('utf-8')):
            buf[i] = ch
    except IndexError:
        # Buffer overflow occurred! Simulate leaking the flag
        return "Buffer Overflow detected! Memory corrupted, leaking flag: SECRET_FLAG_DATA_123"
        
    return "processed safely"

# handler
handle = process_input
