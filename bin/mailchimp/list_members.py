import os
import json
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError

def getlistid(name):
  r = client.lists.get_all_lists()
  for l in r['lists']:
    if l['name'] == name:
      return l['id']

client = MailchimpMarketing.Client()

client.set_config({
  "api_key": os.environ.get('MAILCHIMP_API_KEY'),
  "server": os.environ.get('MAILCHIMP_SERVER')
})

list = getlistid(os.environ.get('AUDIENCE'))

try:
  response = client.lists.get_list_members_info(list, count=1000)
  print(json.dumps(response))
except ApiClientError as error:
  print("Error: {}".format(error.text))
