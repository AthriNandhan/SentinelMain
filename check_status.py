import urllib.request

try:
    with urllib.request.urlopen('http://localhost:8001/api/status/a13cc50c-6e6f-4a4a-aeea-2a52a10e16a2') as response:
        print(f"Status code: {response.getcode()}")
        print(f"Response text: {response.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")