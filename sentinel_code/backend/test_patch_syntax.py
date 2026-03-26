#!/usr/bin/env python3
"""Test if Blue Agent's patched code is syntactically valid."""

from app.agents.blue_agent import blue_agent
from app.models.state import RemediationState

# Create a test state
state = RemediationState(
    code_path="../sandbox/vulnerable_code.py",
    vulnerability_type="SQL_INJECTION",
    exploit_payloads=["' OR '1'='1", "admin' --"]
)

# Get the patched code from blue_agent
fixed_state = blue_agent(state)

# Try to parse it as Python code
print("=== Checking Patch Syntax ===")
print(f"Patch size: {len(fixed_state.patch_diff)} bytes")
print(f"Patch explanation: {fixed_state.patch_explanation}")

try:
    compile(fixed_state.patch_diff, '<string>', 'exec')
    print("✓ Patch is syntactically valid Python")
except SyntaxError as e:
    print(f"✗ SYNTAX ERROR in patch:")
    print(f"  Line {e.lineno}: {e.msg}")
    print(f"  {e.text}")

# Print first 500 chars to inspect
print("\n=== First 500 chars of patch ===")
print(fixed_state.patch_diff[:500])
print("...")
