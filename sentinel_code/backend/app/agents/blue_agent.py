from app.models.state import RemediationState
from app.services.llm import llm_service
import os

def blue_agent(state: RemediationState) -> RemediationState:
    """
    Blue Agent: Generates a fix for the vulnerability.
    """
    print("--- Blue Agent: Patching ---")
    
    with open(state.code_path, "r") as f:
        code_content = f.read()

    prompt = f"""
    You are an expert Secure Code Developer.
    Fix the {state.vulnerability_type} vulnerability in the following code.
    An attacker found this exploit: {state.exploit_payloads[-1] if state.exploit_payloads else 'None'}
    
    Constraints:
    1. Modify ONLY the security-relevant code. Do not remove or change any other functionality (e.g. legacy table support).
    2. Use parameterized queries (e.g. `cursor.execute(query, params)`) instead of string formatting or concatenation.
    3. Ensure minimal code changes. Do not over-engineer.
    
    Code:
    ```python
    {code_content}
    ```
    
    Provide the fixed code. Return ONLY the python code for the fixed file, without markdown formatting or conversational text.
    """

    fixed_code = llm_service.generate_text(prompt)
    
    # Strip markdown code blocks if present
    if "```python" in fixed_code:
        fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
    elif "```" in fixed_code:
        fixed_code = fixed_code.split("```")[1].split("```")[0].strip()
    
    # Store full patched code in state
    state.patch_diff = fixed_code.strip()
    state.patch_explanation = "Applied secure coding practices (parameterized queries)."
    state.iteration_count += 1
    
    return state
