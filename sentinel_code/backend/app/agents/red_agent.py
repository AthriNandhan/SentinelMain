from app.models.state import RemediationState
from app.services.llm import llm_service
from app.core.test_harness import test_harness
from app.core.vulnerability_config import get_payloads_for_type
from app.services.logger import get_logger
import os

def red_agent(state: RemediationState) -> RemediationState:
    """
    Red Agent: Simulates an attack on the vulnerable code.
    Iterates through payloads for the vulnerability type and attempts to exploit.
    """
    logger = get_logger(state.workflow_id) if state.workflow_id else None
    if logger:
        logger.log_and_print("Red Agent", "--- Red Agent: Attacking ---")
    else:
        print("--- Red Agent: Attacking ---")
    
    if not os.path.exists(state.code_path):
        msg = f"Error: File {state.code_path} not found."
        if logger:
            logger.log_and_print("Red Agent", msg)
        else:
            print(msg)
        state.exploit_success = False
        return state

    # Get payloads for this vulnerability type
    PAYLOADS = get_payloads_for_type(state.vulnerability_type)
    if not PAYLOADS:
        msg = f"Error: No payloads configured for vulnerability type: {state.vulnerability_type}"
        if logger:
            logger.log_and_print("Red Agent", msg)
        else:
            print(msg)
        state.exploit_success = False
        return state

    msg = f"Executing payloads ({state.vulnerability_type}) against {state.code_path} via TestHarness..."
    if logger:
        logger.log_and_print("Red Agent", msg)
    else:
        print(msg)
    test_harness.stop_server()  # Ensure clean state
    test_harness.start_server(code_path=state.code_path)
    
    success = False
    successful_payload = None
    
    try:
        for payload in PAYLOADS:
            attempt_msg = f"Trying payload: {payload}"
            if logger:
                logger.log_and_print("Red Agent", attempt_msg)
            else:
                print(attempt_msg)
            result = test_harness.run_attack(payload, vuln_type=state.vulnerability_type)
            
            if result["success"]:
                exploit_msg = f"Exploit VERIFIED! Flag leaked: {result['data']}"
                if logger:
                    logger.log_and_print("Red Agent", exploit_msg)
                else:
                    print(exploit_msg)
                success = True
                successful_payload = payload
                break
            else:
                failure_msg = f"Failed. Output: {result.get('data')} | Error: {result.get('error')}"
                if logger:
                    logger.log_and_print("Red Agent", failure_msg)
                else:
                    print(failure_msg)
                
    finally:
        test_harness.stop_server()

    if success:
        state.exploit_success = True
        state.exploit_payloads.append(successful_payload)
        
        # craft a payload snippet matching the vulnerability type
        # by default, send the raw payload in a JSON field relevant to the vuln
        def make_payload_snippet(vuln_type, payload):
            # payload may already be a dict when formatted by harness
            if isinstance(payload, dict):
                return payload
            if vuln_type == "SQL":
                return {"username": payload, "request_id": "poc_1"}
            elif vuln_type == "XSS":
                return {"comment": payload}
            elif vuln_type == "PATH_TRAVERSAL":
                return {"filename": payload}
            elif vuln_type == "BUFFER_OVERFLOW":
                return {"input": payload}
            elif vuln_type == "INFO_EXPOSURE":
                return {"key": "test", "data": payload}
            elif vuln_type == "XXE":
                return {"xml": payload}
            elif vuln_type == "SSRF":
                return {"url": payload}
            elif vuln_type == "INSECURE_RANDOMNESS":
                return {"user_id": 1, "data": payload}
            elif vuln_type == "RACE_CONDITION":
                return {"data": payload}
            elif vuln_type == "BOLA":
                try:
                    import json as _json
                    return _json.loads(payload)
                except Exception:
                    return {"data": payload}
            elif vuln_type == "HARDCODED_SECRETS":
                return {"data": payload}
            elif vuln_type == "DESERIALIZATION":
                return {"session_data": payload}
            else:
                return {"data": payload}

        poc_payload = make_payload_snippet(state.vulnerability_type, successful_payload)
        poc_content = f"""import requests

# Auto-generated PoC exploit by Red Agent - {state.vulnerability_type}
url = "http://localhost:5000/analyze"
payload = {poc_payload}
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
            
        msg2 = f"PoC written to {poc_path}"
        if logger:
            logger.log_and_print("Red Agent", msg2)
        else:
            print(msg2)
    else:
        msg = "Red Agent: All payloads failed. No exploit found or vulnerability not present."
        if logger:
            logger.log_and_print("Red Agent", msg)
        else:
            print(msg)
        state.exploit_success = False
        # mark as already secure so workflow doesn't leave status pending
        state.verification_status = "PASS"
        state.verification_reasoning = "No successful exploit payloads; target appears secure or not vulnerable."

    return state
