import urllib.request

try:
    with urllib.request.urlopen('http://localhost:8001/api/status/75fa286c-758c-4d60-9de7-e7126ddd0286') as response:
        print(f"Status code: {response.getcode()}")
        print(f"Response text: {response.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")