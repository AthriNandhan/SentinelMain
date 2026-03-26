import urllib.request
import json

data = {
    "code_path": "../../vulnerabilities/5_insecure_deserialization.py",
    "vulnerability_type": "DESERIALIZATION"
}
data = json.dumps(data).encode('utf-8')

req = urllib.request.Request(
    'http://localhost:8001/api/remediate',
    data=data,
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        print('Status code:', response.getcode())
        print('Response text:', response.read().decode('utf-8'))
except Exception as e:
    print('Error:', e)