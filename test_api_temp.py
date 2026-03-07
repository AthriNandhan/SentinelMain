import urllib.request
import json

url = "http://localhost:8001/api/remediate"
data = {"vulnerability_type": "insecure_deserialization"}
json_data = json.dumps(data).encode('utf-8')

try:
    req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        print("Status code:", response.getcode())
        print("Response text:", response.read().decode('utf-8'))
except urllib.request.HTTPError as e:
    print("Status code:", e.code)
    print("Response text:", e.read().decode('utf-8'))
except Exception as e:
    print("Error:", str(e))