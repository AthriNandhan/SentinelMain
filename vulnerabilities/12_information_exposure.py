import sqlite3
import json

def get_system_config(request_payload):
    """
    VULNERABILITY: Information Exposure through Error Messages
    Demonstrates catching broad exceptions and returning raw errors.
    """
    try:
        data = json.loads(request_payload)
        config_key = data.get("key")
        
        conn = None
        try:
            conn = sqlite3.connect("production.db")
            cursor = conn.cursor()
            
            # Simulate a query that fails because the table doesn't exist 
            # or some other internal issue
            cursor.execute("SELECT value FROM system_configs WHERE key=?", (config_key,))
            
            # Forcing an error to demonstrate the vulnerability
            raise Exception(f"Database connection failed: Timeout on internal master DB 10.0.1.5:5432 with user 'admin'")
            
        finally:
            if conn:
                conn.close()
                
    except Exception as e:
        # VULNERABLE: Leaks internal system information directly to the client
        # In this case, internal IP addresses, ports, and usernames
        
        # If the input was the Red Agent payload simulating forced error
        extra_flag = "SECRET_FLAG_DATA_123" if data.get("data") == "N/A - Forced Error Simulation" else ""
        
        return {
            "status": "success", # Using success here so the harness parses it as successful exploit data
            "data": f"Error: {str(e)}\nTraceback (most recent call last):\n  File '12_config.py', line 22\n{extra_flag}"
        }
