import requests
import json

def fetch_remote_image(request_payload):
    """
    VULNERABILITY: Server-Side Request Forgery (SSRF)
    Demonstrates requesting an arbitrary URL based on user input.
    """
    try:
        data = json.loads(request_payload)
        image_url = data.get("url")
        
        # VULNERABLE: Can be used to access internal metadata services 
        # (e.g., 169.254.169.254) or localhost ports.
        
        # Simulating external requests blocking but internal returning the flag
        if "169.254" in image_url or "localhost" in image_url or "127.0.0.1" in image_url:
            return {"status": "success", "data": "Internal API Response: SECRET_FLAG_DATA_123"}
            
        response = requests.get(image_url, timeout=5)
        
        if response.status_code == 200:
            return {"status": "success", "data": "base64_encoded_data_here"}
        else:
            return {"status": "error", "message": f"Failed to fetch image: {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}
