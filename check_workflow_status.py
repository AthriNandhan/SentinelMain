import urllib.request

try:
    with urllib.request.urlopen('http://localhost:8001/api/status/e6baf48d-85de-44c4-9cb6-1105dd72308c') as response:
        print(f"Status code: {response.getcode()}")
        print(f"Response text: {response.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")