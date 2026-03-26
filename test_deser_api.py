import urllib.request
import json

url = "http://localhost:8001/api/remediate"
data = {"code_path": "vulnerabilities/5_insecure_deserialization.py", "vulnerability_type": "DESERIALIZATION"}
json_data = json.dumps(data).encode('utf-8')

try:
    req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        print("Status code:", response.getcode())
        print("Response text:", response.read().decode('utf-8'))
except Exception as e:
    print("Error:", str(e))