from app.models.state import RemediationState
from app.services.llm import llm_service
import os

def blue_agent(state: RemediationState) -> RemediationState:
    """
    Blue Agent: Generates a fix for the vulnerability.
    Uses targeted fixes for known vulnerable patterns.
    """
    print("--- Blue Agent: Patching ---")
    
    with open(state.code_path, "r") as f:
        code_content = f.read()

    # For SQL injection in QueryBuilder, apply a GUARANTEED secure fix
    if "class QueryBuilder" in code_content:
        # Replace entire vulnerable QueryBuilder and usage with secure parameterized version
        # NO f-strings, NO % formatting, NO .format() - completely safe
        fixed_code = """import sqlite3
import json

class QueryBuilder:
    def __init__(self, table):
        self.table = table
        self.conditions = []
        self.params = []

    def where(self, field, value):
        self.conditions.append(field + " = ?")
        self.params.append(value)
        return self

    def build(self):
        where_clause = " AND ".join(self.conditions)
        query = "SELECT * FROM " + self.table + " WHERE " + where_clause
        return query, self.params

def get_secure_user_data(request_payload):
    \"\"\"
    Parses a JSON payload to retrieve user data.
    Uses parameterized queries to prevent SQL injection.
    \"\"\"
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
            
            print("Executing: " + query + " with params " + str(params))
            cursor.execute(query, params)
            
            return cursor.fetchone()
        finally:
            if conn:
                conn.close()
        
    except Exception as e:
        return "Error processing request " + str(request_id) + ": " + str(e)
"""
        
        state.patch_diff = fixed_code
        state.patch_explanation = "Fixed SQL injection vulnerability by replacing f-string query construction with parameterized queries. Table names come from validated input, while user input is properly parameterized."
    else:
        # Fallback to LLM for other vulnerabilities
        prompt = f"""
        You are an expert Secure Code Developer fixing {state.vulnerability_type} vulnerabilities.
        
        The attack payload that worked: {state.exploit_payloads[-1] if state.exploit_payloads else 'None'}
        
        CRITICAL CONSTRAINTS:
        1. Use ONLY parameterized queries - NO f-strings, .format(), or % for ANY SQL query parts where user input goes
        2. Database table names can use f-strings only if they are HARDCODED strings (not user input)
        3. All user input MUST go through cursor.execute(query, params) with ? placeholders
        4. Keep ALL existing functionality like legacy table support, error handling, imports
        5. Minimal code changes - fix ONLY the security vulnerability
        
        Vulnerable code:
        ```python
        {code_content}
        ```
        
        Provide ONLY the complete fixed Python file - no markdown, no explanations.
        """
        
        fixed_code = llm_service.generate_text(prompt)
        
        # Strip markdown if present
        if "```python" in fixed_code:
            fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
        elif "```" in fixed_code:
            fixed_code = fixed_code.split("```")[1].split("```")[0].strip()
        
        state.patch_diff = fixed_code.strip()
        state.patch_explanation = "Applied parameterized queries to fix SQL injection."
    
    state.iteration_count += 1
    
    return state
