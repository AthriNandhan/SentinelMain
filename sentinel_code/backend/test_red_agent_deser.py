#!/usr/bin/env python
"""Test Red Agent directly on deserialization vulnerability."""
import sys
import os

sys.path.insert(0, '.')

from app.models.state import RemediationState
from app.agents.red_agent import red_agent

print("\n=== Testing Red Agent on Deserialization ===\n")

# Create state pointing to vulnerabilities file
state = RemediationState(
    code_path="../../vulnerabilities/5_insecure_deserialization.py",  # relative to backend
    vulnerability_type="DESERIALIZATION",
    iteration_count=0
)

print(f"Code path: {state.code_path}")
print(f"Absolute: {os.path.abspath(state.code_path)}")
print(f"Exists: {os.path.exists(state.code_path)}")

try:
    result_state = red_agent(state)
    
    print("\n--- Red Agent Results ---")
    print(f"Exploit Success: {result_state.exploit_success}")
    print(f"Exploit Payloads: {result_state.exploit_payloads}")
    print(f"Verification Status: {result_state.verification_status}")
    print(f"Reasoning: {str(result_state.verification_reasoning)}")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
