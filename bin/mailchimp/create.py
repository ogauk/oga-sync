import os
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError

client = MailchimpMarketing.Client()
client.set_config({
  "api_key": os.environ.get('MAILCHIMP_API_KEY'),
  "server": os.environ.get('MAILCHIMP_SERVER')
})

def create():
  r = client.lists.create_list({'name': 'OGA Members from GOLD', 'email_type_option': False, 'contact': {'company': 'Old Gaffers Association', 'address1': '2 Tythe Barn Way', 'address2': '', 'city': 'South Woodham Ferrers', 'state': 'Essex', 'zip': 'CM35PX', 'country': 'GB', 'phone': ''}, 'permission_reminder': 'You are receiving this email as an OGA member.', 'use_archive_bar': True, 'campaign_defaults': {'from_name': 'Old Gaffers Association', 'from_email': 'secretary@oga.org.uk', 'subject': '', 'language': 'en'}})
  r = client.lists.get_all_lists()
  print(r['total_items'])
  for l in r['lists']:
    print(l['name'])
    print(l['id'])
  return r


def remove(id):
  response = client.lists.delete_list(id)

try:
  r = create()
except ApiClientError as error:
  print("Error: {}".format(error.text))

