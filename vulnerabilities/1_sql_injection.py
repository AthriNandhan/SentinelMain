import sqlite3
import json

def login_user(request_payload):
    """
    VULNERABILITY: SQL Injection
    Demonstrates unsanitized user input being concatenated directly into a SQL query.
    This is an example change
    """
    try:
        data = json.loads(request_payload)
        username = data.get("username")
        password = data.get("password")
        
        conn = None
        try:
            conn = sqlite3.connect("production.db")
            cursor = conn.cursor()
            
            # VULNERABLE: Direct string formatting
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            print(f"Executing: {query}")
            
            cursor.execute(query)
            users = cursor.fetchall()
            
            if users:
                # Return the data column (index 4) which contains the flag for the admin user
                return {"status": "success", "data": users[0][4] if len(users[0]) > 4 else str(users[0])}
            return {"status": "error", "message": "Invalid credentials"}
            
        finally:
            if conn:
                conn.close()
                
    except Exception as e:
        return {"status": "error", "message": str(e)}
