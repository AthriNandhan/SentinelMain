#!/usr/bin/env python3
"""Test if the patched code actually works."""

from app.agents.blue_agent import blue_agent
from app.models.state import RemediationState
import os
import sys
import sqlite3
import tempfile

# Generate the patch
state = RemediationState(
    code_path="../sandbox/vulnerable_code.py",
    vulnerability_type="SQL_INJECTION",
    exploit_payloads=["' OR '1'='1", "admin' --"]
)

fixed_state = blue_agent(state)
patch_code = fixed_state.patch_diff

# Create a temp test file for the patched code
with tempfile.TemporaryDirectory() as tmpdir:
    testfile = os.path.join(tmpdir, "test_patched_code.py")
    with open(testfile, "w") as f:
        f.write(patch_code)
    
    # Try to import it
    print("=== Testing Patched Code Import ===")
    try:
        # Add temp dir to sys.path
        sys.path.insert(0, tmpdir)
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_patched_code", testfile)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✓ Patch imported successfully")
        
        # Try to call the function
        print("\n=== Testing Patched Function ===")
        # Set up test DB
        import json
        
        try:
            os.remove("production.db")
        except:
            pass
        
        conn = sqlite3.connect("production.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, active INTEGER, data TEXT)")
        cursor.execute("INSERT INTO users (username, password, active, data) VALUES ('alice', 'password123', 1, 'Public Profile Data')")  
        cursor.execute("INSERT INTO users (username, password, active, data) VALUES ('admin', 'admin123', 1, 'SECRET_FLAG_DATA_123')")
        conn.commit()
        conn.close()
        
        # Test normal query
        payload = json.dumps({"username": "alice", "request_id": "test1"})
        result = module.get_secure_user_data(payload)
        print(f"Normal query result: {result}")
        
        # Test SQL injection
        payload_injection = json.dumps({"username": "' OR '1'='1", "request_id": "test2"})
        result_injection = module.get_secure_user_data(payload_injection)
        print(f"SQL injection attempt result: {result_injection}")
        
        if "alice" in str(result) and "admin" not in str(result_injection):
            print("✓ Patch appears to WORK - normal query OK, injection blocked")
        else:
            print("✗ Patch might not work as expected")
            
    except Exception as e:
        print(f"✗ Error testing patched code: {e}")
        import traceback
        traceback.print_exc()
