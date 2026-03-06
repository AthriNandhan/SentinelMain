#!/usr/bin/env python
"""Test the deserialization vulnerability through the complete workflow."""
import sys
import os

sys.path.insert(0, '.')

from app.graph.workflow import app as workflow_app
from app.models.state import RemediationState

print("\n" + "="*70)
print("DESERIALIZATION VULNERABILITY WORKFLOW TEST")
print("="*70)

# Use the actual vulnerability file
code_path = os.path.join(
    os.path.dirname(__file__), 
    "..", "..", 
    "vulnerabilities", 
    "5_insecure_deserialization.py"
)

initial_state = RemediationState(
    code_path=code_path,
    vulnerability_type="DESERIALIZATION",
    iteration_count=0
)

print(f"\nStarting workflow for: {os.path.basename(code_path)}")
print(f"Vulnerability type: DESERIALIZATION\n")

try:
    final_state = workflow_app.invoke(initial_state)
    
    print("\n--- RESULTS ---")
    print(f"Exploit Success: {final_state.get('exploit_success')}")
    print(f"Exploit Payloads: {final_state.get('exploit_payloads')}")
    print(f"Verification Status: {final_state.get('verification_status')}")
    print(f"Iteration Count: {final_state.get('iteration_count')}")
    print(f"Verification Reasoning: {final_state.get('verification_reasoning')}")
    
    success = (
        final_state.get('exploit_success') and 
        final_state.get('verification_status') in ['PASS', 'pending']
    )
    
    print("\n" + "="*70)
    if success:
        print("✓ DESERIALIZATION WORKFLOW SUCCESSFUL")
    else:
        print("✗ DESERIALIZATION WORKFLOW FAILED")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
