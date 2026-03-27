import sqlite3
import json
import base64
import os
import hashlib
from urllib.parse import quote
from html import escape

class QueryBuilder:
    def __init__(self, table):
        self.table = table
        self.conditions = []

    def where(self, field, value):
        self.conditions.append((field, value))
        return self

    def build(self):
        where_clause = []
        values = []
        for field, value in self.conditions:
            where_clause.append(f"{field} = ?")
            values.append(value)
        return f"SELECT * FROM {self.table} WHERE {' AND '.join(where_clause)}", values

def get_secure_user_data(data):
    username = data.get("username")
    request_id = data.get("request_id")
    
    target_table = "users"
    if data.get("is_legacy"):
        target_table = "legacy_users_v1"

    qb = QueryBuilder(target_table)
    qb.where("username", username)
    qb.where("active", 1)
    
    query, values = qb.build()
    
    conn = sqlite3.connect("production.db")
    cursor = conn.cursor()
    cursor.execute(query, values)
    return cursor.fetchone()

def process_comment(data):
    comment = data.get("comment", "")
    sanitized = escape(comment)
    template = f"""
    <div class="user-comment">
        {sanitized}
    </div>
    """
    return template

def read_user_file(data):
    filename = data.get("filename", "")
    base_dir = "/var/www/uploads/"
    
    if not filename or len(filename) > 255:
        raise ValueError("Invalid filename")
        
    if not os.path.abspath(base_dir + filename).startswith(base_dir):
        raise ValueError("Invalid directory")
        
    try:
        with open(base_dir + filename, "r") as file:
            return file.read()
    except Exception as e:
        return str(e)

def load_user_session(data):
    session_cookie = data.get("session_data")
    
    if not session_cookie or len(session_cookie) > 4096:
        return "Invalid session data"
        
    try:
        decoded_data = base64.b64decode(session_cookie)
        return hashlib.sha256(decoded_data).hexdigest()
    except Exception as e:
        return str(e)

def handle(request_payload):
    try:
        data = json.loads(request_payload)
        
        if "username" in