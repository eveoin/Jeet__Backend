import requests

# Make a GET request to obtain the CSRF token
response = requests.get('http://localhost:5000/signup')
csrf_token = response.cookies.get('csrf_access_token')

# Include the CSRF token in the headers for subsequent requests
headers = {'X-CSRFToken': csrf_token}

# Make a POST request with the CSRF token
data = {'username': 'example', 'password': 'password'}
response = requests.post('http://localhost:5000/login', json=data, headers=headers)

print(response.json())


dc6f8cf55952d4550b2a54a1a79b6398