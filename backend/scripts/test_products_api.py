import requests

r = requests.post('http://localhost:8000/api/auth/login', json={'email': 'test@advisor.com', 'password': 'TestPassword123!'})
print('Login:', r.status_code, r.json())
token = r.json()['access_token']

p = requests.get(
    'http://localhost:8000/api/products',
    headers={'Authorization': f'Bearer {token}'},
    params={'tax_bracket': 0.30, 'time_horizon': 'long'}
)
print('Products status:', p.status_code)
print('Body:', p.text[:2000])
