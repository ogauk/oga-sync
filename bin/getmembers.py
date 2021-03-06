import os
import requests

headers = {
    'authority': 'oga-gold.org.uk',
    'origin': 'https://oga-gold.org.uk',
    'content-type': 'application/x-www-form-urlencoded',
}

params = (
    ('operation', 'logout'),
)

data = {
  'username': os.environ.get('USER'),
  'password': os.environ.get('PASS')
}

response = requests.post('https://oga-gold.org.uk/login.php', headers=headers, params=params, data=data)
print(response)
