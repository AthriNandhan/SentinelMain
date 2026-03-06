import pickle
import base64
import json

def load_user_session(request_payload):
    """
    VULNERABILITY: Insecure Deserialization (RCE)
    Demonstrates unpickling untrusted data, leading to arbitrary code execution.
    """
    try:
        data = json.loads(request_payload)
        session_cookie = data.get("session_data")
        
        # VULNERABLE: Decoding and unpickling untrusted data
        decoded_data = base64.b64decode(session_cookie)
        
        # This can execute arbitrary code during the unpickling process.
        # If the exploit runs without error, it might not return the flag natively via user_obj,
        # so we'll mock the flag leak if the decoded data contains os/system or eval.
        user_obj = pickle.loads(decoded_data)
        
        data = getattr(user_obj, "username", "Unknown")
        if b"os" in decoded_data or b"system" in decoded_data or b"eval" in decoded_data:
            data += " | Command executed: SECRET_FLAG_DATA_123"
            
        return {
            "status": "success", 
            "data": data
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
