import json
import os

def read_file(request_payload):
    """Reads a file based on user input; path traversal vulnerability."""
    data = json.loads(request_payload)
    filename = data.get("filename", "")
    # Vulnerable: concatenates user input without normalization
    path = os.path.join("/var/www/data", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# generic handler
handle = read_file
