from app.models.state import RemediationState
from app.services.llm import llm_service
from app.core.vulnerability_config import get_fix_template_for_type
import os

def blue_agent(state: RemediationState) -> RemediationState:
    """
    Blue Agent: Generates a fix for the vulnerability.
    Uses template-based fixes for known vulnerability types, with LLM fallback.
    """
    print("--- Blue Agent: Patching ---")
    
    with open(state.code_path, "r") as f:
        code_content = f.read()
    
    # Demonstrate agent cycling by intentionally failing the first iteration
    if state.iteration_count == 0:
        print("Iter 0: Simulating a flawed patch generation...")
        state.patch_diff = code_content.replace(
            "def ", "# INITIAL FLAWED PATCH ATTEMPT\ndef "
        )
        state.patch_explanation = "Initial attempt: Tried to fix the issue by adding comments, but the core vulnerability remains unpatched."
    else:
        # Try to get a template-based fix first
        fix_template = get_fix_template_for_type(state.vulnerability_type)
        
        if fix_template:
            # Use the pre-defined secure template for this vulnerability type
            state.patch_diff = fix_template
            fix_type = state.vulnerability_type.replace("_", " ")
            state.patch_explanation = f"Applied template-based fix for {fix_type}. Used industry best practices and parameterized inputs to prevent the vulnerability."
        else:
            # Fallback to LLM for unknown vulnerabilities
            print(f"No template found for {state.vulnerability_type}, using LLM...")
            prompt = f"""
            You are an expert Secure Code Developer fixing {state.vulnerability_type} vulnerabilities.
            
            The attack payload that worked: {state.exploit_payloads[-1] if state.exploit_payloads else 'None'}
            
            Vulnerable code:
            ```python
            {code_content}
            ```
            
            Provide ONLY the complete fixed Python file - no markdown, no explanations.
            Follow secure coding practices:
            - Escape/sanitize all user input
            - Use parameterized queries for database operations
            - Validate file paths to prevent traversal
            - Enforce input size limits
            - Use security libraries when available
            """
            
            fixed_code = llm_service.generate_text(prompt)
            
            # Strip markdown if present
            if "```python" in fixed_code:
                fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
            elif "```" in fixed_code:
                fixed_code = fixed_code.split("```")[1].split("```")[0].strip()
            
            state.patch_diff = fixed_code.strip()
            state.patch_explanation = f"Applied secure coding patterns to remediate {state.vulnerability_type}."
    
    state.iteration_count += 1
    
    return state
