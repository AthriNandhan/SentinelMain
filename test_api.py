import urllib.request
import json

try:
    data = json.dumps({'vulnerability_type': 'insecure_deserialization'}).encode('utf-8')
    req = urllib.request.Request('http://localhost:8001/api/remediate', data=data, headers={'Content-Type': 'application/json'})
    response = urllib.request.urlopen(req, timeout=10)
    print('Status:', response.getcode())
    print('Response:', response.read().decode('utf-8'))
except Exception as e:
    print('Error:', e)