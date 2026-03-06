# Select in Dropdown: SQL Injection
import json
import sqlite3

class QueryBuilder:
    def __init__(self, table):
        self.table = table
        self.wheres = []

    def add_condition(self, field, value):
        # "Safe" stringify? No, this just casts to string.
        # It doesn't escape quotes.
        val_str = str(value)
        self.wheres.append(f"{field} = '{val_str}'")

    def to_sql(self):
        where_clause = " AND ".join(self.wheres)
        return f"SELECT * FROM {self.table} WHERE {where_clause}"

def process_search(request_json):
    """
    Level: HARD
    Vulnerability: Second-Order SQL Injection / Logic Flaw
    Why: The vulnerability is inside a helper class, and the input
    comes from a JSON object where types might be ambiguous.
    """
    try:
        data = json.loads(request_json)
        
        # Logic Flaw: User can control the table name via a hidden flag
        table = "products"
        if data.get("admin_debug_mode"):
            table = "users" # Privilege Escalation risk
            
        qb = QueryBuilder(table)
        
        search_term = data.get("query")
        category = data.get("category")
        
        # The injection point
        qb.add_condition("name", search_term)
        
        if category:
            qb.add_condition("category", category)

        sql = qb.to_sql()
        
        conn = sqlite3.connect("production.db")
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.close()
        return result
        
    except Exception as e:
        return {"error": "Search failed"}

def handle(payload):
    """
    Handle function for Flask app integration.
    Expects JSON payload with search parameters.
    """
    try:
        result = process_search(payload)
        if isinstance(result, dict):
            return str(result)
        elif result:
            return str(result)
        return "No results"
    except Exception as e:
        return f"Error: {str(e)}"
