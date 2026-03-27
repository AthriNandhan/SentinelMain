from app.models.state import RemediationState
from app.services.llm import llm_service
from app.services.logger import get_logger
import os

def blue_agent(state: RemediationState) -> RemediationState:
    """
    Blue Agent: Generates a consolidated fix for all discovered vulnerabilities.
    """
    logger = get_logger(state.workflow_id) if state.workflow_id else None
    if logger:
        logger.log_and_print("Blue Agent", "--- Blue Agent: Batch Patching ---")
    else:
        print("--- Blue Agent: Batch Patching ---")
    
    with open(state.code_path, "r") as f:
        code_content = f.read()
    
    # Demonstrate agent cycling by intentionally failing the first iteration
    if state.iteration_count == 0:
        msg = "Iter 0: Simulating a flawed consolidated patch generation..."
        if logger:
            logger.log_and_print("Blue Agent", msg)
        else:
            print(msg)
        state.patch_diff = code_content.replace(
            "def ", "# INITIAL FLAWED BATCH PATCH ATTEMPT\ndef "
        )
        state.patch_explanation = "Initial attempt: Tried to fix the issues by adding comments, but the core vulnerabilities remain unpatched."
    else:
        # Build prompt for all successful exploits
        vulns_to_fix = [vt for vt, success in state.vulnerability_checklist.items() if success]
        
        msg = f"Using LLM to fix multiple vulnerabilities: {', '.join(vulns_to_fix)}..."
        if logger:
            logger.log_and_print("Blue Agent", msg)
        else:
            print(msg)
            
        payloads_text = "\\n".join([f"- {vt}: {state.successful_payloads[vt]}" for vt in vulns_to_fix])
        
        prompt = f"""
        You are an expert Secure Code Developer.
        Your task is to fix MULTIPLE vulnerabilities in the provided code SIMULTANEOUSLY.
        
        The code is vulnerable to the following: {', '.join(vulns_to_fix)}
        
        Successful attack payloads that worked against the current code:
        {payloads_text}
        
        Vulnerable code:
        ```python
        {code_content}
        ```
        
        Provide ONLY the complete fixed Python file - no markdown, no explanations. Do not include any text before or after the code block.
        Follow secure coding practices to fix ALL listed vulnerabilities at once:
        - Escape/sanitize all user input (HTML escaping for XSS)
        - Use parameterized queries for database operations to prevent SQL Injection
        - Validate file paths to prevent traversal
        - Enforce input size limits for buffer overflows
        - Use safe libraries and patterns
        """
        
        fixed_code = llm_service.generate_text(prompt)
        
        # Strip markdown if present
        if "```python" in fixed_code:
            fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
        elif "```" in fixed_code:
            fixed_code = fixed_code.split("```")[1].split("```")[0].strip()
        
        state.patch_diff = fixed_code.strip()
        state.patch_explanation = f"Applied unified secure coding patterns to remediate: {', '.join(vulns_to_fix)}."
    
    state.iteration_count += 1
    
    return state
