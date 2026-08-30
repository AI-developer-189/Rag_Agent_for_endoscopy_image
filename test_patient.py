import json, urllib.request, urllib.error, sys

url = 'http://localhost:8000/api/patients'
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNzg2NzIxNjY4LCJpYXQiOjE3ODY2MzUyNjh9.ac4r6AVdVUecU8rU2Ilf7oMWYdZBhbPtM6_uIs1vNFo'
data = json.dumps({'full_name': 'John Doe', 'age': 30, 'sex': 'Male'}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
})
try:
    resp = urllib.request.urlopen(req)
    print(f'Status: {resp.status}')
    print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f'HTTP Error: {e.code}')
    body = e.read().decode('utf-8')
    print('Body:', repr(body))
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')