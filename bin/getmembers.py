import os
import requests
from io import StringIO
import csv

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

s = requests.Session()

response = s.post('https://oga-gold.org.uk/login.php', headers=headers, params=params, data=data)
response = s.get('https://oga-gold.org.uk/members.php?quick_filter=&quick_filter_operator=Contains', headers=headers)
response = s.get('https://oga-gold.org.uk/members.php?operation=ecsv', headers=headers)
f = StringIO(response.text)
reader = csv.reader(f, delimiter=',')
for row in reader:
    print('\t'.join(row))

