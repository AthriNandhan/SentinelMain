import sqlite3
import json
import base64
import os
import html

class QueryBuilder:
    def __init__(self, table):
        self.table = table

def get_secure_user_data(data):
    """Secure SQL function (parameterized query building)."""
    username = data.get("username", "")
    request_id = data.get("request_id", "")
    
    conn = sqlite3.connect("production.db")
    cursor = conn.cursor()
    # secure: uses parameterized query to prevent SQL injection
    query = "SELECT * FROM users WHERE active = 1 AND username = ?"
    cursor.execute(query, (username,))
    return cursor.fetchone()

def process_comment(data):
    """Secure XSS function"""
    comment = data.get("comment", "")
    
    # properly sanitizes user input using HTML escaping
    sanitized = html.escape(comment)
    
    # stores sanitized input in template
    template = """
    <div class="user-comment">
        {}
    </div>
    """.format(sanitized)
    return template

def read_user_file(data):
    """Secure Path Traversal function"""
    filename = data.get("filename", "")
    base_dir = "/var/www/uploads/"
    
    # securely validates file path using os.path.abspath and os.path.commonprefix
    full_path = os.path.abspath(os.path.join(base_dir, filename))
    common_prefix = os.path.commonprefix([full_path, base_dir])
    
    if common_prefix != base_dir:
        raise ValueError("Invalid directory")
        
    try:
        # Mocking the file read for sandbox purposes
        if "../" in filename or "..\\" in filename:
            return "root:x:0:0:root:/root:/bin/bash"
        return "Normal file content"
    except Exception as e:
        return str(e)

def load_user_session(data):
    """Secure Deserialization"""
    session_cookie = data.get("session_data")
    
    try:
        # uses json instead of pickle for secure deserialization
        decoded_data = json.loads(base64.b64decode(session_cookie).decode('utf-8'))
        return decoded_data.get("username", "Unknown")
    except Exception as e:
        return f"Error: {str(e)}"

def handle(request_payload):
    """Mega Dispatcher. Routes to correct vulnerability based on payload structure."""
    try:
        data = json.loads(request_payload)
        
        # enforces input size limit to prevent