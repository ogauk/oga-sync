import os
import requests
import time
import json

headers = {
    'Authorization': 'key='+os.environ.get('FCM_API_KEY'),
    'Content-Type': 'application/json',
}

data = {
 "to": "/topics/news",
 "notification": {
    "title": time.strftime('it is %H:%M GMT', time.gmtime()),
    "body": "or it was when we sent this"
  },
  "data": None
}

print(headers)
print(data)

response = requests.post('https://fcm.googleapis.com/fcm/send', headers=headers, data=json.dumps(data))
print(response)
print(response.text)

