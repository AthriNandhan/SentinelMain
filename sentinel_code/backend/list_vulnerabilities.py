#!/usr/bin/env python3
"""
Utility to display available vulnerability types in the Sentinel system.
"""

from app.core.vulnerability_config import VULNERABILITIES

def list_vulnerabilities():
    """Print all available vulnerability types and their details."""
    print("=" * 70)
    print("AVAILABLE VULNERABILITY TYPES IN SENTINEL")
    print("=" * 70)
    
    for idx, (vuln_code, vuln_config) in enumerate(VULNERABILITIES.items(), 1):
        print(f"\n{idx}. {vuln_code}")
        print(f"   Name: {vuln_config['display_name']}")
        print(f"   Description: {vuln_config['description']}")
        print(f"   Attack Payloads: {len(vuln_config['payloads'])}")
        print(f"   Example Payloads:")
        for payload in vuln_config['payloads'][:2]:
            truncated = payload[:60] + "..." if len(payload) > 60 else payload
            print(f"      - {truncated}")
    
    print("\n" + "=" * 70)
    print("USAGE IN CODE:")
    print("=" * 70)
    print("""
from app.models.state import RemediationState
from app.graph.workflow import app as workflow_app

# Create initial state with vulnerability type
state = RemediationState(
    code_path="path/to/vulnerable/code.py",
    vulnerability_type="SQL",  # Use SHORT_CODE from above
    iteration_count=0
)

# Run the workflow
result = workflow_app.invoke(state)
""")

if __name__ == "__main__":
    list_vulnerabilities()
