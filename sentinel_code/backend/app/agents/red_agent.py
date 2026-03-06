from app.models.state import RemediationState
from app.services.llm import llm_service
from app.core.test_harness import test_harness
from app.core.vulnerability_config import get_payloads_for_type
import os

def red_agent(state: RemediationState) -> RemediationState:
    """
    Red Agent: Simulates an attack on the vulnerable code.
    Iterates through payloads for the vulnerability type and attempts to exploit.
    """
    print("--- Red Agent: Attacking ---")
    
    if not os.path.exists(state.code_path):
        print(f"Error: File {state.code_path} not found.")
        state.exploit_success = False
        return state

    # Get payloads for this vulnerability type
    PAYLOADS = get_payloads_for_type(state.vulnerability_type)
    if not PAYLOADS:
        print(f"Error: No payloads configured for vulnerability type: {state.vulnerability_type}")
        state.exploit_success = False
        return state

    print(f"Executing payloads ({state.vulnerability_type}) against {state.code_path} via TestHarness...")
    test_harness.start_server(code_path=state.code_path)
    
    success = False
    successful_payload = None
    
    try:
        for payload in PAYLOADS:
            print(f"Trying payload: {payload}")
            result = test_harness.run_attack(payload, vuln_type=state.vulnerability_type)
            
            if result["success"]:
                print(f"Exploit VERIFIED! Flag leaked: {result['data']}")
                success = True
                successful_payload = payload
                break
            else:
                print(f"Failed. Output: {result.get('data')} | Error: {result.get('error')}")
                
    finally:
        test_harness.stop_server()

    if success:
        state.exploit_success = True
        state.exploit_payloads.append(successful_payload)
        
        poc_content = f"""import requests

# Auto-generated PoC exploit by Red Agent - {state.vulnerability_type}
url = "http://localhost:5000/analyze"
payload = {{"username": "{successful_payload}", "request_id": "poc_1"}}
try:
    response = requests.post(url, json=payload, timeout=5)
    print("Status:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", e)
"""
        poc_path = os.path.join(os.path.dirname(state.code_path), "poc_exploit.py")
        with open(poc_path, "w") as f:
            f.write(poc_content)
            
        print(f"PoC written to {poc_path}")
    else:
        print("Red Agent: All payloads failed. No exploit found or vulnerability not present.")
        state.exploit_success = False
        # mark as already secure so workflow doesn't leave status pending
        state.verification_status = "PASS"
        state.verification_reasoning = "No successful exploit payloads; target appears secure or not vulnerable."

    return state
