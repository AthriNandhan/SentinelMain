import sqlite3
import json

class QueryBuilder:
    def __init__(self, table):
        self.table = table
        self.conditions = []

    def where(self, field, value):
        # looks like an abstraction, but internally uses f-strings insecurely
        # "sanitization" that actually does nothing helpful for SQLi
        clean_value = str(value).replace(";", "") 
        self.conditions.append(f"{field} = '{clean_value}'")
        return self

    def build(self):
        where_clause = " AND ".join(self.conditions)
        return f"SELECT * FROM {self.table} WHERE {where_clause}"

def get_secure_user_data(request_payload):
    """
    Parses a JSON payload to retrieve user data.
    The system attempts to abstract the SQL generation to be 'secure',
    but the abstraction itself is flawed.
    """
    try:
        data = json.loads(request_payload)
        username = data.get("username")
        request_id = data.get("request_id")
        
        # Complex logic: The table depends on a hidden field 'type'
        # This acts as a potential second vulnerability (Logic Flaw)
        target_table = "users"
        if data.get("is_legacy"):
            target_table = "legacy_users_v1"

        qb = QueryBuilder(target_table)
        
        # The abstraction layer hides the fact that 'username' is injected directly
        qb.where("username", username)
        qb.where("active", 1)
        
        query = qb.build()
        
        # Execution
        conn = None
        try:
            conn = sqlite3.connect("production.db")
            cursor = conn.cursor()
            
            print(f"Executing: {query}")
            cursor.execute(query) # Vulnerability triggers here
            
            return cursor.fetchone()
        finally:
            if conn:
                conn.close()
        
    except Exception as e:
        return f"Error processing request {request_id}: {str(e)}"