from app.models.state import RemediationState
from app.services.llm import llm_service
import os

def red_agent(state: RemediationState) -> RemediationState:
    """
    Red Agent: Simulates an attack on the vulnerable code.
    """
    print("--- Red Agent: Attacking ---")
    
    # Read the vulnerable code
    if not os.path.exists(state.code_path):
        print(f"Error: File {state.code_path} not found.")
        state.exploit_success = False
        return state

    with open(state.code_path, "r") as f:
        code_content = f.read()

    prompt = f"""
    You are an expert Red Team security researcher. 
    Analyze the following code for a {state.vulnerability_type} vulnerability.
    
    Code:
    ```python
    {code_content}
    ```
    
    The database is SQLite.
    The goal is to extract the 'data' field from the 'users' table where username='admin'.
    The query is constructed using f-strings.
    
    If the vulnerability exists, provide a specific input string (payload) that exploits it.
    The payload should break out of the query and return the admin's data.
    Do NOT include markdown formatting (backticks). 
    Return ONLY the raw payload string.
    If no vulnerability is found, return "SAFE".
    """

    response = llm_service.generate_text(prompt).strip()
    
    # Strip markdown if present (e.g., ```, ```json)
    if response.startswith("```"):
        response = response.split("```")[1]
        if response.startswith("json"):
            response = response[4:]
        elif response.startswith("sql"):
            response = response[3:]
        response = response.strip()
    
    if "SAFE" in response:
        state.exploit_success = False
        print("Red Agent: Vulnerability not found or safe.")
    else:
        print(f"Generated Exploit Payload: {response}")
        
        # Determine strict logic: Execute the payload
        from app.core.test_harness import TestHarness
        harness = TestHarness()
        
        print(f"Executing payload against {state.code_path}...")
        result = harness.run_attack(state.code_path, response)
        
        if result["error"]:
             print(f"Execution Error: {result['error']}")
        
        # If we got the flag, it's a success
        if result["success"]:
            state.exploit_success = True
            state.exploit_payloads.append(response)
            print(f"Exploit VERIFIED! Flag leaked: {result['data']}")
        else:
            print(f"Exploit FAILED with payload: {response}")
            print(f"Response data: {result['data']}")
            print(f"Error: {result['error']}")
            
            # Fallback for demonstration purposes if LLM fails
            print("Attempting fallback payload: admin' --")
            fallback_payload = "admin' --"
            fallback_result = harness.run_attack(state.code_path, fallback_payload)
            
            if fallback_result["success"]:
                print(f"Fallback Exploit VERIFIED! Flag leaked: {fallback_result['data']}")
                state.exploit_success = True
                state.exploit_payloads.append(fallback_payload)
            else:
                 state.exploit_success = False
                 print("Fallback also failed.")

    return state
