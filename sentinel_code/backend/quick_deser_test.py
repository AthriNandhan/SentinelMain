#!/usr/bin/env python
"""Quick test to verify deserialization works with module reload."""
import sys
import os
import shutil
import time
import json

# Add backend to path
sys.path.insert(0, os.path.abspath('.'))

from app.core.test_harness import test_harness
from app.core.vulnerability_config import get_payloads_for_type

print("\n=== Testing Insecure Deserialization ===\n")

# Get payloads
payloads = get_payloads_for_type("DESERIALIZATION")
print(f"Payloads for DESERIALIZATION: {len(payloads)} configured")

# Copy code to sandbox and start server
print("\nStarting server with deserialization code...")
code_path = os.path.join(os.path.dirname(__file__), "..", "..", "vulnerabilities", "5_insecure_deserialization.py")
print(f"Using: {code_path}")

try:
    test_harness.start_server(code_path=code_path)
    
    # Test each payload
    for i, payload in enumerate(payloads, 1):
        print(f"\n[{i}/{len(payloads)}] Testing: {payload[:50]}...")
        result = test_harness.run_attack(payload, vuln_type="DESERIALIZATION")
        
        print(f"  success: {result['success']}")
        print(f"  data: {result['data'][:100] if result['data'] else None}...")
        print(f"  flag found: {'SECRET_FLAG_DATA_123' in str(result.get('data', ''))}")
        
        if result['success']:
            print("  ✓ PASS")
        else:
            print("  ✗ FAIL")
            
finally:
    test_harness.stop_server()
    print("\nServer stopped.\n")
