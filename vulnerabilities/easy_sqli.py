# Select in Dropdown: SQL Injection
import sqlite3
import json

def get_user_data(username):
    """
    Level: EASY
    Vulnerability: SQL Injection
    Why: Direct string concatenation of user input into a query.
    """
    conn = sqlite3.connect("production.db")
    cursor = conn.cursor()
    
    # The classic vulnerability
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    
    print(f"Executing: {query}")
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result

def handle(payload):
    """
    Handle function for Flask app integration.
    Expects JSON payload with 'username' field.
    """
    try:
        data = json.loads(payload)
        username = data.get("username", "")
        result = get_user_data(username)
        if result:
            return str(result)
        return "No data found"
    except Exception as e:
        return f"Error: {str(e)}"
