# Select in Dropdown: Insecure Deserialization
import pickle
import base64
import os
import logging
from typing import Any, Dict, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CacheManager:
    """
    Manages session caching for the application.
    Implements a custom serialization protocol for 'efficiency'.
    """
    def __init__(self, cache_dir: str = "/tmp/app_cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _serialize(self, obj: Any) -> bytes:
        """
        Internal method to serialize objects.
        Uses pickle because it handles complex Python objects better than JSON.
        """
        try:
            return pickle.dumps(obj)
        except Exception as e:
            logger.error(f"Serialization failed: {e}")
            raise

    def _deserialize(self, data: bytes) -> Any:
        """
        Internal method to deserialize objects.
        """
        try:
            # Vulnerability: Unsafe deserialization of untrusted data
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Deserialization failed: {e}")
            return None

    def get_session(self, session_token: str) -> Optional[Dict]:
        """
        Retrieves a session object based on a token.
        The token is a base64 encoded string of the serialized session data.
        """
        logger.info(f"Attempting to retrieve session: {session_token[:10]}...")
        
        try:
            # Decode the token
            decoded_data = base64.b64decode(session_token)
            
            # Deep inspection (Simulating business logic)
            if len(decoded_data) < 10:
                logger.warning("Session token too short")
                return None

            # Retrieve from cache
            session_obj = self._deserialize(decoded_data)
            
            if not isinstance(session_obj, dict):
                logger.error("Invalid session format")
                return None

            # Validate session expiry (Simulated)
            if "expiry" in session_obj:
               # complex logic ignored for brevity
               pass

            return session_obj

        except Exception as e:
            logger.error(f"Session retrieval error: {e}")
            return None

    def save_session(self, session_data: Dict) -> str:
        """
        Saves a session and returns the token.
        """
        serialized = self._serialize(session_data)
        return base64.b64encode(serialized).decode('utf-8')

class SessionHandler:
    def __init__(self):
        self.cache = CacheManager()

    def handle_request(self, request: Dict):
        """
        Main entry point for request handling.
        """
        auth_header = request.get("Authorization")
        if not auth_header:
            return {"status": 401, "message": "Unauthorized"}

        token = auth_header.replace("Bearer ", "")
        
        # EXPERT LEVEL CHALLENGE:
        # The vulnerability is not in this file's direct execution path for a simple script,
        # but in the deep usage of `pickle.loads` inside `CacheManager`.
        # Attackers can construct a malicious pickle payload, base64 encode it, 
        # and send it as the Bearer token to achieve RCE.
        
        session = self.cache.get_session(token)
        
        if session:
            return {"status": 200, "message": f"Welcome back, {session.get('username')}"}
        else:
            return {"status": 403, "message": "Invalid Session"}

def handle(payload):
    """
    Handle function for Flask app integration.
    Expects JSON payload with 'Authorization' header (as data).
    """
    try:
        data = json.loads(payload)
        handler = SessionHandler()
        result = handler.handle_request(data)
        return str(result) if result else "No session"
    except Exception as e:
        return f"Error: {str(e)}"

# Example of how the application is run
if __name__ == "__main__":
    handler = SessionHandler()
    
    # Normal usage
    user_session = {"username": "alice", "role": "user", "expiry": "2025-01-01"}
    token = handler.cache.save_session(user_session)
    print(f"Generated Token: {token}")
    
    response = handler.handle_request({"Authorization": f"Bearer {token}"})
    print(response)
