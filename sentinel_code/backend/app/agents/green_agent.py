from app.models.state import RemediationState
from app.services.llm import llm_service

def green_agent(state: RemediationState) -> RemediationState:
    """
    Green Agent: Verifies the code by analyzing the patch.
    """
    print("--- Green Agent: Verifying ---")
    
    prompt = f"""
    You are a Security Auditor.
    Review the following code for {state.vulnerability_type}.
    
    Code:
    ```python
    {state.patch_diff}
    ```
    
    Task:
    1. Verify if the code is secure against {state.vulnerability_type}.
    2. CRITICAL: Verify that NO existing functionality (helper functions, classes, imports) was removed or broken.
       If the patch removes unrelated code (e.g., helper functions used by other modules), it must FAIL.
    
    Output strictly in the following format:
    Reasoning: <Detailed analysis of security AND regression check>
    Status: <PASS or FAIL>
    """
    
    response = llm_service.generate_text(prompt).strip()
    
    response = llm_service.generate_text(prompt).strip()
    
    # ----------------------------------------------------
    # NEW: EXECUTION-BASED VERIFICATION
    # ----------------------------------------------------
    from app.core.test_harness import TestHarness
    harness = TestHarness()
    
    print("\nExecuting Test Harness on patched code...")
    results = harness.verify_fix(state.patch_diff)
    
    verified = results["regression_passed"] and results["security_passed"]
    
    # Update reasoning with actual execution results
    execution_reasoning = "\n".join(results["details"])
    print(f"Test Results:\n{execution_reasoning}")
    
    if verified:
        status = "PASS"
        reasoning = f"Automated Tests PASSED.\n{execution_reasoning}\n\nLLM Review: {response}"
    else:
        status = "FAIL"
        reasoning = f"Automated Tests FAILED.\n{execution_reasoning}\n\nLLM Review: {response}"

    state.verification_status = status
    state.verification_reasoning = reasoning
        
    print(f"Verification Result: {state.verification_status}")
    print(f"Reasoning: {reasoning}")
    
    return state
