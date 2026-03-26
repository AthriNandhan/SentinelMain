import os
import json
import subprocess

def ping_target(request_payload):
    """
    VULNERABILITY: OS Command Injection
    Demonstrates unsanitized user input executing arbitrary shell commands.
    """
    try:
        data = json.loads(request_payload)
        hostname = data.get("hostname", "8.8.8.8")
        
        # VULNERABLE: Direct command concatenation with shell=True
        command = f"ping -c 4 {hostname}"
        print(f"Executing: {command}")
        
        # Allows command chaining like '8.8.8.8; rm -rf /'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        output = result.stdout
        # Simulate exposing the flag when arbitrary commands are executed
        if ";" in hostname or "&" in hostname or "|" in hostname:
            output += "\nSECRET_FLAG_DATA_123"
            
        return {
            "status": "success",
            "data": output
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
