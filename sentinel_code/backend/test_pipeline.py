from app.graph.workflow import app as workflow_app
from app.models.state import RemediationState

def test_pipeline():
    print("Testing End-to-End Pipeline...")
    initial_state = RemediationState(
        code_path="../sandbox/vulnerable_code.py",
        vulnerability_type="SQL Injection",
        iteration_count=0
    )

    final_state = workflow_app.invoke(initial_state)
    print("\n--- Final State ---")
    print(f"Exploit Success: {final_state.get('exploit_success')}")
    print(f"Verification Status: {final_state.get('verification_status')}")
    print(f"Iteration Count: {final_state.get('iteration_count')}")
    print(f"Reasoning: {final_state.get('verification_reasoning')}")

if __name__ == "__main__":
    test_pipeline()
