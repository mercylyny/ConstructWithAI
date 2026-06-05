import json
import urllib.request

base = 'http://127.0.0.1:8000'

# Register user
url = base + '/auth/register'
payload = {'email':'test-reset@example.com','password':'TestPassword123','name':'Test User'}
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type':'application/json'})
print('Registering user...')
print(urllib.request.urlopen(req).read().decode())

# Request SMS reset
url2 = base + '/auth/forgot-password'
payload2 = {'email':'test-reset@example.com','via':'sms','phone':'+15551234567'}
req2 = urllib.request.Request(url2, data=json.dumps(payload2).encode('utf-8'), headers={'Content-Type':'application/json'})
print('Requesting SMS reset...')
print(urllib.request.urlopen(req2).read().decode())
