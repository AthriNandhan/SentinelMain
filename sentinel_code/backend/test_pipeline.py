from app.graph.workflow import app as workflow_app
from app.models.state import RemediationState
from app.core.vulnerability_config import get_vulnerability_config

# initial list only included the four demo vulnerabilities; add all configured types
VULNERABILITY_TYPES = [
    "SQL",
    "XSS",
    "PATH_TRAVERSAL",
    "BUFFER_OVERFLOW",
    "INFO_EXPOSURE",
    "XXE",
    "BOLA",
    "INSECURE_RANDOMNESS",
    "RACE_CONDITION",
    "HARDCODED_SECRETS",
    "DESERIALIZATION",
    "SSRF",
]

def test_single_pipeline(vuln_type):
    """Test the remediation pipeline for a single vulnerability type."""
    print(f"\n{'='*70}")
    print(f"Testing: {vuln_type}")
    config = get_vulnerability_config(vuln_type)
    print(f"Name: {config['display_name']}")
    print(f"Description: {config['description']}")
    print(f"{'='*70}")
    
    initial_state = RemediationState(
        code_path="../sandbox/vulnerable_code.py",
        vulnerability_type=vuln_type,
        iteration_count=0
    )
    initial_state.workflow_id = f"pipeline_{vuln_type}"

    try:
        final_state = workflow_app.invoke(initial_state)
        
        print(f"\n--- Results for {vuln_type} ---")
        print(f"Exploit Success: {final_state.get('exploit_success')}")
        print(f"Verification Status: {final_state.get('verification_status')}")
        print(f"Iteration Count: {final_state.get('iteration_count')}")
        print(f"Reasoning: {final_state.get('verification_reasoning')}")
        
        return {
            "vulnerability": vuln_type,
            "exploit_success": final_state.get('exploit_success'),
            "verification_status": final_state.get('verification_status'),
            "iteration_count": final_state.get('iteration_count')
        }
    except Exception as e:
        print(f"\n✗ ERROR testing {vuln_type}: {str(e)}")
        return {
            "vulnerability": vuln_type,
            "exploit_success": None,
            "verification_status": "ERROR",
            "iteration_count": 0,
            "error": str(e)
        }

def test_all_pipelines():
    """Test the remediation pipeline for all vulnerability types."""
    print("\n" + "="*70)
    print("SENTINEL END-TO-END PIPELINE TEST - ALL VULNERABILITIES")
    print("="*70)
    
    results = []
    for vuln_type in VULNERABILITY_TYPES:
        # choose sandbox file based on type
        file_map = {
            "SQL": "vulnerable_sql.py",
            "XSS": "vulnerable_xss.py",
            "PATH_TRAVERSAL": "vulnerable_path_traversal.py",
            "BUFFER_OVERFLOW": "vulnerable_buffer_overflow.py",
            # generic fallback for the rest; they all honour same sandbox file
            "INFO_EXPOSURE": "vulnerable_code.py",
            "XXE": "vulnerable_code.py",
            "BOLA": "vulnerable_code.py",
            "INSECURE_RANDOMNESS": "vulnerable_code.py",
            "RACE_CONDITION": "vulnerable_code.py",
            "HARDCODED_SECRETS": "vulnerable_code.py",
            "DESERIALIZATION": "vulnerable_code.py",
            "SSRF": "vulnerable_code.py",
        }
        path = "../sandbox/" + file_map.get(vuln_type, "vulnerable_code.py")
        print(f"\n--- using file: {path}")
        # override default path by temporarily mutating initial_state inside helper
        initial_state = RemediationState(
            code_path=path,
            vulnerability_type=vuln_type,
            iteration_count=0
        )
        initial_state.workflow_id = f"pipeline_{vuln_type}"
        try:
            final_state = workflow_app.invoke(initial_state)
            print(f"\n--- Results for {vuln_type} ---")
            print(f"Exploit Success: {final_state.get('exploit_success')}")
            print(f"Verification Status: {final_state.get('verification_status')}")
            print(f"Iteration Count: {final_state.get('iteration_count')}")
            print(f"Reasoning: {final_state.get('verification_reasoning')}")
            
            results.append({
                "vulnerability": vuln_type,
                "exploit_success": final_state.get('exploit_success'),
                "verification_status": final_state.get('verification_status'),
                "iteration_count": final_state.get('iteration_count')
            })
        except Exception as e:
            print(f"\n✗ ERROR testing {vuln_type}: {str(e)}")
            results.append({
                "vulnerability": vuln_type,
                "exploit_success": None,
                "verification_status": "ERROR",
                "iteration_count": 0,
                "error": str(e)
            })
    
    # summary
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for result in results:
        status_icon = "✓" if result.get("verification_status") == "PASS" else "✗"
        exploit_icon = "✓" if result.get("exploit_success") else "✗"
        print(f"{status_icon} {result['vulnerability']:20} | Exploit: {exploit_icon} | Verification: {result.get('verification_status', 'N/A'):6} | Iterations: {result.get('iteration_count', 0)}")
    
    print("\n" + "="*70)
    passed = sum(1 for r in results if r.get("verification_status") == "PASS")
    total = len(results)
    print(f"TOTAL: {passed}/{total} vulnerabilities successfully remediated")
    print("="*70)

if __name__ == "__main__":
    test_all_pipelines()
