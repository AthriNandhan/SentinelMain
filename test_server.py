import urllib.request

try:
    response = urllib.request.urlopen('http://localhost:8001/docs', timeout=5)
    print('Status:', response.getcode())
    print('Server is responding')
except Exception as e:
    print('Error:', e)