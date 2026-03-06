import json
import os

def read_file(request_payload):
    """Reads a file based on user input; path traversal vulnerability."""
    data = json.loads(request_payload)
    filename = data.get("filename", "")
    
    # Simulate Path Traversal exploit succeeding by returning the flag
    if "../" in filename or "..\\" in filename or ".." in filename:
        return f"root:x:0:0:root:/root:/bin/bash\nSECRET_FLAG_DATA_123\nContent of {filename}"
        
    path = os.path.join("/var/www/data", filename)
    # mock normal file content
    return f"Normal file content for {filename}"

# generic handler
handle = read_file
