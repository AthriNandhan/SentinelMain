import os
import json

def read_user_report(request_payload):
    """
    VULNERABILITY: Path Traversal (Local File Inclusion)
    Demonstrates unsafe file access utilizing user-controlled paths.
    """
    try:
        data = json.loads(request_payload)
        filename = data.get("filename")
        
        base_dir = "/var/log/myapp/reports/"
        
        # VULNERABLE: User can specify '../../../../etc/passwd' to break out of base_dir
        file_path = os.path.join(base_dir, filename)
        
        print(f"Reading file: {file_path}")
        
        if not os.path.exists(file_path):
            # Simulate a successful path traversal reading sensitive data
            if "../" in filename or "..\\" in filename:
                return {"status": "success", "data": "root:x:0:0:root:/root:/bin/bash\nSECRET_FLAG_DATA_123"}
            return {"status": "error", "message": "File not found"}
             
        with open(file_path, "r") as f:
            content = f.read()
            
        return {"status": "success", "data": content}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
