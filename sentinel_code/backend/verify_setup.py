import sys
import os

# Add backend to path
# Get the directory containing this script (e.g., .../sentinel_code/backend)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the backend directory to sys.path so app modules can be imported
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app.models.state import RemediationState
from app.graph.workflow import app as workflow_app

def test_workflow():
    print("Initializing state...")
    # Use absolute path to ensure agents can find it
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # vulnerable_code.py is in the project root, which is two levels up from sentinel_code/backend
    project_root = os.path.dirname(os.path.dirname(current_dir))
    vulnerable_file = os.path.join(project_root, "vulnerable_code.py")
    
    initial_state = RemediationState(
        code_path=vulnerable_file,
        vulnerability_type="SQL Injection"
    )
    
    print("Running workflow...")
    try:
        final_state_dict = workflow_app.invoke(initial_state)
        final_state = RemediationState(**final_state_dict)
        
        print("\nWorkflow completed successfully!")
        print(f"Iteration Count: {final_state.iteration_count}")
        print(f"Exploit Success: {final_state.exploit_success}")
        print(f"Verification Status: {final_state.verification_status}")
        
    except Exception as e:
        print(f"Workflow failed: {e}")
        raise e

if __name__ == "__main__":
    test_workflow()
