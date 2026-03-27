import sqlite3
import json
import base64
import pickle
import os

class QueryBuilder:
    def __init__(self, table):
        self.table = table
        self.conditions = []

    def where(self, field, value):
        # insecure: injects unescaped user input directly into the query
        clean_value = str(value).replace(";", "")
        self.conditions.append(f"{field} = '{clean_value}'")
        return self

    def build(self):
        where_clause = " AND ".join(self.conditions)
        return f"SELECT * FROM {self.table} WHERE {where_clause}"

def get_secure_user_data(data):
    """Vulnerable SQL function (insecure query building)."""
    username = data.get("username")
    request_id = data.get("request_id")
    
    target_table = "users"
    if data.get("is_legacy"):
        target_table = "legacy_users_v1"

    qb = QueryBuilder(target_table)
    qb.where("username", username)
    qb.where("active", 1)
    
    query = qb.build()
    
    conn = sqlite3.connect("production.db")
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone()

def process_comment(data):
    """Vulnerable XSS function"""
    comment = data.get("comment", "")
    
    # Inadequately filtering script tags
    sanitized = comment.replace("<script>", "")
    
    # Store directly in template without escaping Context
    template = f"""
    <div class="user-comment">
        {sanitized}
    </div>
    """
    return template

def read_user_file(data):
    """Vulnerable Path Traversal function"""
    filename = data.get("filename", "")
    base_dir = "/var/www/uploads/"
    
    # Inadequate defense: only checks if it starts with base_dir, but allows ../ anywhere else
    full_path = base_dir + filename
    
    if not full_path.startswith("/var/www/"):
        raise ValueError("Invalid directory")
        
    try:
        # Mocking the file read for sandbox purposes
        if "../" in filename or "..\\\\" in filename:
            return "root:x:0:0:root:/root:/bin/bash"
        return "Normal file content"
    except Exception as e:
        return str(e)

def load_user_session(data):
    """Vulnerable Insecure Deserialization"""
    session_cookie = data.get("session_data")
    
    decoded_data = None
    exploit_detected = False
    result_text = "Unknown"

    try:
        decoded_data = base64.b64decode(session_cookie)
        try:
            user_obj = pickle.loads(decoded_data)
            result_text = getattr(user_obj, "username", "Unknown")
        except Exception as inner_e:
            result_text = f"pickle error: {inner_e}"
    except Exception:
        pass

    raw_bytes = session_cookie.encode('utf-8')
    if decoded_data:
        raw_bytes = decoded_data
    if b"os" in raw_bytes or b"system" in raw_bytes or b"eval" in raw_bytes:
        exploit_detected = True
    if exploit_detected:
        result_text += " | Command executed: SECRET_FLAG_DATA_123"

    return result_text


def handle(request_payload):
    """Mega Dispatcher. Routes to correct vulnerability based on payload structure."""
    try:
        data = json.loads(request_payload)
        
        if "username" in data:
            return get_secure_user_data(data)
        elif "comment" in data:
            return process_comment(data)
        elif "filename" in data:
            return read_user_file(data)
        elif "session_data" in data:
            # wait, the other script returned a dict {"status": ..., "data": ...} 
            # let's return it directly, the sandbox app.py wraps it anyways
            return load_user_session(data)
            
        return "Unknown payload type"
    except Exception as e:
        return f"Error processing: {str(e)}"
