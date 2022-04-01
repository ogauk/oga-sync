import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError

client = MailchimpMarketing.Client()
client.set_config({
  "api_key": os.environ.get('MAILCHIMP_API_KEY'),
  "server": os.environ.get('MAILCHIMP_SERVER')
})

def getlistid(name):
  r = client.lists.get_all_lists()
  for l in r['lists']:
    if l['name'] == name:
      return l['id']

def create_areas(list):
  response = client.lists.create_list_interest_category(list, {"title": "Area", "type": "checkboxes"})
  id = response['id']
  for area in ['Bristol Channel', 'Dublin Bay', 'East Coast', 'North East', 'North Wales', 'North West', 'Northern Ireland', 'Scotland', 'Solent', 'South West']:
    client.lists.create_interest_category_interest(list, id, {"name": area})

def delete_areas(list, id):
  response = client.lists.delete_interest_category(list, id)

def create_statuses(list):
  response = client.lists.create_list_interest_category(list, {"title": "Status", "type": "radio"})
  id = response['id']
  for status in ['Exempt','Paid Up','Not Paid']:
    client.lists.create_interest_category_interest(list, id, {"name": status})

def create_membership_types(list):
  response = client.lists.create_list_interest_category(list, {"title": "Membership Type", "type": "radio"})
  id = response['id']
  for m in ['Single','Family','Honorary','Junior','Overseas','Associate']:
    client.lists.create_interest_category_interest(list, id, {"name": m})

def create_payment_methods(list):
  response = client.lists.create_list_interest_category(list, {"title": "Payment Method", "type": "radio"})
  id = response['id']
  for m in ['Exempt', 'Direct Debit', 'Cheque', 'Dublin Bay', 'PayPal', 'Credit Transfer']:
    client.lists.create_interest_category_interest(list, id, {"name": m})

def create_options(list):
  response = client.lists.create_list_interest_category(list, {"title": "Options", "type": "checkboxes"})
  id = response['id']
  for m in ['Interested in events for small boats']:
    client.lists.create_interest_category_interest(list, id, {"name": m})

def create_primary(list):
  response = client.lists.create_list_interest_category(list, {"title": "Family Member", "type": "radio"})
  id = response['id']
  for m in ['Primary','Other']:
    client.lists.create_interest_category_interest(list, id, {"name": m})

def create_contact_methods(list):
  response = client.lists.create_list_interest_category(list, {"title": "Contact Method", "type": "checkboxes"})
  id = response['id']
  for m in ['Email','Phone']:
    client.lists.create_interest_category_interest(list, id, {"name": m})

def create_interests(list):
  create_areas(list)
  create_statuses(list)
  create_payment_methods(list)
  create_membership_types(list)
  create_options(list)
  create_primary(list)
  create_contact_methods(list)

def create_merge_fields(list):
  response = client.lists.add_list_merge_field(list, {"name": "Salutation", "tag": "SALUTATION", "type": "text"})
  response = client.lists.add_list_merge_field(list, {"name": "Reason for joining", "tag": "REASON", "type": "text"})
  response = client.lists.add_list_merge_field(list, {"name": "When Joined", "tag": "JOINED", "type": "date"})
  response = client.lists.add_list_merge_field(list, {"name": "Mobile", "tag": "MOBILE", "type": "phone"})
  response = client.lists.add_list_merge_field(list, {"name": "Member Number", "tag": "MEMBER", "type": "number"})
  response = client.lists.add_list_merge_field(list, {"name": "ID", "tag": "GOLD", "type": "number"})
  response = client.lists.add_list_merge_field(list, {"name": "GDPR", "tag": "GDPR", "type": "text"})

try:
  list = getlistid(os.environ.get('AUDIENCE'))
  create_interests(list)
  create_merge_fields(list)
  response = client.lists.get_list_merge_fields(list)
  for m in response['merge_fields']:
    print(m['tag'], m['name'], m['type'])
    print(m)
except ApiClientError as error:
  print("Error: {}".format(error.text))

