#!/usr/bin/env python
"""Test if the fixed code actually prevents SQL injection"""
import sys
import tempfile
import os
from app.agents.blue_agent import blue_agent
from app.core.test_harness import test_harness
from app.models.state import RemediationState

print("=== Testing Security of Blue Agent Fix ===\n")

# Get the fix
state = RemediationState(
    code_path='../sandbox/vulnerable_code.py',
    vulnerability_type='SQL Injection',
    exploit_success=True,
    exploit_payloads=['admin\' --', "' OR '1'='1"],
    iteration_count=0
)

print("1. Getting Blue Agent fix...")
result = blue_agent(state)
print("   ✓ Fix generated")

# Test with test harness
print("\n2. Testing fix with test harness...")
test_results = test_harness.verify_fix(result.patch_diff, security_payloads=["admin' --", "' OR '1'='1"])

print("   Regression Test:", "PASS" if test_results["regression_passed"] else "FAIL")
print("   Security Test:", "PASS" if test_results["security_passed"] else "FAIL")

for detail in test_results["details"]:
    print("   -", detail)

# Summary
print("\n=== SUMMARY ===")
if test_results["regression_passed"] and test_results["security_passed"]:
    print("✓ Fix is SECURE and functional")
    sys.exit(0)
else:
    print("✗ Fix FAILED tests")
    sys.exit(1)
