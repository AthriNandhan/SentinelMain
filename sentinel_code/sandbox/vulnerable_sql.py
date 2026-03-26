import sqlite3
import json

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

def get_secure_user_data(request_payload):
    """Vulnerable SQL function (insecure query building)."""
    try:
        data = json.loads(request_payload)
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
        print(f"Executing: {query}")
        cursor.execute(query)
        return cursor.fetchone()
    except Exception as e:
        return f"Error processing request {request_id}: {e}"

# generic handler entrypoint used by sandbox/app.py
handle = get_secure_user_data