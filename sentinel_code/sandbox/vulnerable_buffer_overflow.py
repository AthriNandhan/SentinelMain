import json

def process_input(request_payload):
    """Simulates unsafe buffer handling that may raise an overflow error."""
    data = json.loads(request_payload)
    user_input = data.get("input", "")
    # Vulnerable: writes directly into fixed-size bytearray
    buf = bytearray(10)
    for i, ch in enumerate(user_input.encode('utf-8')):
        # will throw IndexError if input too long
        buf[i] = ch
    return "processed"

# handler
handle = process_input
