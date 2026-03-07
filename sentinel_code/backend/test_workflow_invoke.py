#!/usr/bin/env python
"""Test workflow.invoke directly."""
import sys
import os

sys.path.insert(0, '.')

from app.models.state import RemediationState
from app.graph.workflow import app as workflow_app

print("\n=== Testing Workflow Invoke ===\n")

initial_state = RemediationState(
    code_path="C:\\Projects\\Sentinel\\vulnerabilities\\5_insecure_deserialization.py",
    vulnerability_type="DESERIALIZATION",
    iteration_count=0
)

print(f"Initial state: {initial_state}")

try:
    print("Calling workflow_app.invoke...")
    final_state_dict = workflow_app.invoke(initial_state)
    print(f"Final state: {final_state_dict}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
