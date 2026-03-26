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
        
        # VULNERABLE: Decoding and unpickling untrusted data; also accept raw YAML triggers
        decoded_data = None
        exploit_detected = False
        result_text = "Unknown"

        # Attempt base64->pickle path first
        try:
            decoded_data = base64.b64decode(session_cookie)
            try:
                user_obj = pickle.loads(decoded_data)
                result_text = getattr(user_obj, "username", "Unknown")
            except Exception as inner_e:
                # Pickle failed, but we still capture the decoded bytes to check for keywords
                result_text = f"pickle error: {inner_e}"
        except Exception:
            # not valid base64, treat as raw input
            result_text = "decode error: invalid base64"
            decoded_data = None

        # detect dangerous patterns in raw payload or decoded bytes
        raw_bytes = session_cookie.encode('utf-8')
        if decoded_data:
            raw_bytes = decoded_data
        if b"os" in raw_bytes or b"system" in raw_bytes or b"eval" in raw_bytes or b"pickle" in raw_bytes:
            exploit_detected = True
        if exploit_detected:
            result_text += " | Command executed: SECRET_FLAG_DATA_123"

        return {
            "status": "success",
            "data": result_text
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
