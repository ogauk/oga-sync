import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError

def get_interests(list):
  config = {}
  response = client.lists.get_list_interest_categories(list, count=100)
  for category in response['categories']:
    response = client.lists.list_interest_category_interests(list, category['id'], count=100)
    group = {}
    for interest in response['interests']:
      group[interest['name']] = interest['id']
    config[category['title']] = {'id': category['id'], 'interests': group}
  return config

def getlistid(name):
  r = client.lists.get_all_lists()
  for l in r['lists']:
    if l['name'] == name:
      return l['id']

try:
  client = MailchimpMarketing.Client()
  client.set_config({
    "api_key": os.environ.get('MAILCHIMP_API_KEY'),
    "server": os.environ.get('MAILCHIMP_SERVER')
  })

  list = getlistid(os.environ.get('AUDIENCE'))
  config = get_interests(list)
  contact_method = config['Contact Method']['id']
  email = config['Contact Method']['interests']['Email']
  response = client.lists.create_segment(list, {'name': 'Members without email',
    'options': {'match': 'any', 'conditions': [
        {'condition_type': 'Interests', 'field': 'interests-'+contact_method, 'op': 'interestnotcontains', 'value': [email]}
    ]
  }}) 
  response = client.lists.create_segment(list, {'name': 'All Members with email',
    'options': {'match': 'any', 'conditions': [
        {'condition_type': 'Interests', 'field': 'interests-'+contact_method, 'op': 'interestcontains', 'value': [email]}
    ]
  }}) 
  area = config['Area']['id']
  for area_name, area_id in config['Area']['interests'].items():
    print(area_name, area_id)
    response = client.lists.create_segment(list, {'name': area_name+' members with email',
      'options': {'match': 'all', 'conditions': [
        {'condition_type': 'Interests', 'field': 'interests-'+contact_method, 'op': 'interestcontains', 'value': [email]},
        {'condition_type': 'Interests', 'field': 'interests-'+area, 'op': 'interestcontains', 'value': [area_id]},
      ]
    }}) 
except ApiClientError as error:
  print("Error: {}".format(error.text))

