#!/usr/bin/env python
"""Test if Blue Agent produces a secure fix"""
import sys
from app.agents.blue_agent import blue_agent
from app.core.ast_analyzer import analyze_ast
from app.models.state import RemediationState

print("=== Testing Blue Agent Fix ===\n")

# Create test state
state = RemediationState(
    code_path='../sandbox/vulnerable_code.py',
    vulnerability_type='SQL Injection',
    exploit_success=True,
    exploit_payloads=['admin\' --'],
    iteration_count=0
)

# Run Blue Agent
print("1. Running Blue Agent...")
result = blue_agent(state)
print(f"   ✓ Generated patch ({len(result.patch_diff)} bytes)")

# Check for parameterized queries
print("\n2. Checking for secure parameterized queries...")
has_param_execute = 'cursor.execute(query, params)' in result.patch_diff
print(f"   {'✓' if has_param_execute else '✗'} Uses cursor.execute(query, params): {has_param_execute}")

# Check AST for vulnerabilities
print("\n3. Running AST analysis...")
ast_errors = analyze_ast(result.patch_diff)
if ast_errors:
    print(f"   ✗ AST FAILED with errors:")
    for error in ast_errors:
        print(f"      - {error}")
else:
    print("   ✓ AST analysis PASSED")

# Summary
print("\n=== SUMMARY ===")
if has_param_execute and not ast_errors:
    print("✓ Blue Agent fix appears SECURE")
    sys.exit(0)
else:
    print("✗ Blue Agent fix STILL HAS ISSUES")
    sys.exit(1)
