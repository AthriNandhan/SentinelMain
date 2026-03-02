import sqlite3
import json

class QueryBuilder:
    def __init__(self, table):
        self.table = table
        self.conditions = []

    def where(self, field, value):
        self.conditions.append((field, value))
        return self

    def build(self):
        where_clause = []
        params = []
        for field, value in self.conditions:
            where_clause.append(f"{field} = ?")
            params.append(value)
        where_clause_str = " AND ".join(where_clause)
        return f"SELECT * FROM {self.table} WHERE {where_clause_str}", params

def get_secure_user_data(request_payload):
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
        
        query, params = qb.build()
        
        conn = None
        try:
            conn = sqlite3.connect("production.db")
            cursor = conn.cursor()
            
            print(f"Executing: {query} with params {params}")
            cursor.execute(query, params)
            
            return cursor.fetchone()
        finally:
            if conn:
                conn.close()
        
    except Exception as e:
        return f"Error processing request {request_id}: {str(e)}"