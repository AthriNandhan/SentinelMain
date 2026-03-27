from app.graph.workflow import app as workflow_app
from app.models.state import RemediationState
from app.core.vulnerability_config import VULNERABILITIES
import pprint
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_batch():
    initial_state = RemediationState(
        code_path="../sandbox/mega_vulnerable.py",
        target_vulnerabilities=list(VULNERABILITIES.keys()),
        iteration_count=0
    )
    initial_state.workflow_id = "test_batch_1"
    
    print("Starting Batch Pipeline Test...")
    final_state = workflow_app.invoke(initial_state)
    
    print("\\n--- BATCH TEST RESULTS ---")
    print(f"Iteration Count: {final_state.get('iteration_count')}")
    print(f"Verification Status: {final_state.get('verification_status')}")
    print(f"Verification Reasoning:\\n{final_state.get('verification_reasoning')}")
    
    print("\\nChecklist of discovered vulnerabilities:")
    for vuln, status in final_state.get('vulnerability_checklist', {}).items():
        if status:
            print(f"- [VULNERABLE] {vuln}: payload -> {final_state.get('successful_payloads', {}).get(vuln, [''])[0]}")
        else:
            print(f"- [SECURE] {vuln}")

if __name__ == "__main__":
    test_batch()
