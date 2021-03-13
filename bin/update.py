import os
import sys
import csv
import hashlib
import json
import iso3166
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError

excludes = {}
if  'EXCLUDE' in os.environ:
  excludes = json.loads(os.environ.get('EXCLUDE'))

audience_data = {}

def address(member):
  addr1 = member['Address1'].strip()
  if member['Address2'] != '':
    addr1 = addr1 + ', ' + member['Address2'].strip()
  r = { 'addr1': addr1, 'city': member['Town'].strip(), 'state': member['County'].strip(), 'zip': member['Postcode'].strip() }
  if member['Address3'] == '':
    r['addr2'] = ''
  else:
    r['addr2'] = member['Address3'].strip()
  if member['Country'] == '':
    r['country'] = 'GB'
  elif member['Country'] == 'United Kingdom':
    r['country'] = 'GB'
  elif member['Country'] == 'Eire':
    r['country'] = 'IE'
  elif len(member['Country']) == 2:
    r['country'] = iso3166.countries_by_alpha2[member['Country'].upper()].alpha2
  elif len(member['Country']) == 3:
    r['country'] = iso3166.countries_by_alpha3[member['Country'].upper()].alpha2
  else:
    r['country'] = iso3166.countries_by_name[member['Country'].upper()].alpha2
  if member['Postcode'] == '' and member['Country'] == 'France':
    x = member['Address2'].split(' ')
    if len(x)==2 and x[0].isnumeric():
      r['addr1'] = member['Address1']
      r['zip'] = x[0]
      r['city'] = x[1]
    x = member['Town'].split(' ')
    if len(x)==2 and x[0].isnumeric():
      r['zip'] = x[0]
      r['city'] = x[1]
  elif member['County'] == '' and member['Country'] == 'USA':
    x = member['Postcode'].split(' ')
    if len(x)==2:
      r['state'] = x[0]
      r['zip'] = x[1]
  return r

def addAddress(merge_fields, member):
  addr = address(member)
  if addr['addr1'] != '' and addr['city'] != '' and addr['zip'] != '':
    merge_fields['ADDRESS'] = addr
  else:
    merge_fields['ADDRESS'] = ''

def addJoined(merge_fields, member):
  if member['Year Joined'] == '':
    merge_fields['JOINED'] = ''
  elif member['Year Joined'] == None:
    merge_fields['JOINED'] = ''
  else:
    merge_fields['JOINED'] = member['Year Joined']+'-01-01'

def add_area(interests, member):
  areas = audience_data['Area']
  for area in areas:
    interests[areas[area]] = area == member['Area']

def add_payment_methods(interests, member):
  payment_methods = audience_data['Payment Method']
  if member['Payment Method'] == None:
    interests[payment_methods['PayPal']] = True
  elif member['Payment Method'] == '':
    interests[payment_methods['PayPal']] = True
  else:
    interests[payment_methods[member['Payment Method']]] = True

def add_membership_types(interests, member):
  membership_types = audience_data['Membership Type']
  if member['Membership Type'] == None:
    interests[membership_types['Single']] = True
  elif member['Membership Type'] == '':
    interests[membership_types['Single']] = True
  else:
    interests[membership_types[member['Membership Type']]] = True

def add_statuses(interests, member):
  statuses = audience_data['Status']
  if member['Membership Type'] == None:
    interests[statuses['Not Paid']] = True
  elif member['Membership Type'] == '':
    interests[statuses['Not Paid']] = True
  else:
    interests[statuses[member['Status']]] = True

def build_data(member):
    small_boats = audience_data['Options']['Interested in events for small boats'];
    primary = audience_data['Family Member']['Primary'];
    use_email = audience_data['Contact Method']['Email'];
    interests = {
       small_boats: member['Trailer'] == 'true', # Small Boat Events
       primary: member['Primary'] == 'true' or member['Primary'] == None, # Family Member
       use_email: member['Email'] != '' # contact via email
    }
    add_payment_methods(interests, member)
    add_area(interests, member)
    add_membership_types(interests, member)
    add_statuses(interests, member)
    merge_fields = {
        'SALUTATION': member['Salutation'], 
        'FNAME': member['Firstname'].strip(),
        'LNAME': member['Lastname'].strip(),
        'PHONE': member['Telephone'],
        'MOBILE': member['Mobile'],
        'MEMBER': int(member['Member Number']),
        'REASON': member['Reason For Joining'],
        'GOLD': int(member['ID'])
    }
    if merge_fields['REASON'] == None:
      merge_fields['REASON'] = ''
    addAddress(merge_fields, member),
    addJoined(merge_fields, member),
    gdpr = member['GDPR'] == 'true' # TODO more fine grained
    return {
      "status": "subscribed",
      "merge_fields": merge_fields,
      "interests": interests,
      #"marketing_permissions": [
      #  {'marketing_permission_id': '4b8ac61884', 'enabled': gdpr},
      #  {'marketing_permission_id': 'b48f96106f', 'enabled': gdpr},
      #  {'marketing_permission_id': '12f8e21b1c', 'enabled': gdpr}
      #]
    }


def add(list, email, member):
  print('add', email)
  data = build_data(member)
  data['email_address'] = email
  try:
    response = client.lists.add_list_member(list, data)
  except ApiClientError as error:
    e = json.loads(error.text)
    print(e['title'])
    if e['title'] == 'Invalid Resource':
      print("Error: {}".format(error.text))
      try:
        del data['merge_fields']['ADDRESS']
        response = client.lists.add_list_member(list, data)
      except ApiClientError as error:
        print("Error: {}".format(error.text))
        print("%s\t%s" % (member['ID'], member['Lastname']))
    elif e['title'] == 'Member Exists':
      data['email_address'] = member['ID']+'@oga.org.uk'
      try:
        response = client.lists.add_list_member(list, data)
      except ApiClientError as error:
        print("Error: {}".format(error.text))
        print("%s\t%s" % (member['ID'], member['Lastname']))
    else:
      print("Error: {}".format(error.text))
      print("%s\t%s" % (member['ID'], member['Lastname']))

def same(old, new):
  if json.dumps(old, sort_keys=True) == json.dumps(new, sort_keys=True):
    return True
  print('changed')
  return False

def same_interests(complete, partial):
  for key in complete:
    if key in partial:
      if complete[key] != partial[key]:
        return False
    elif complete[key]:
      return False
    else:
      pass
  return True

def same_permissions(old, new):
  for p in old:
    for q in new:
      if p['marketing_permission_id'] == q['marketing_permission_id']:
        if p['enabled'] != q['enabled']:
          return False
  return True

def has_changed(old, new):
  if same(old['merge_fields'], new['merge_fields']) == False:
    return True
  if same_interests(old['interests'], new['interests']) == False:
    return True
  #if same_permissions(old['marketing_permissions'], new['marketing_permissions']) == False:
  #  print(old['marketing_permissions'])
  #  print(new['marketing_permissions'])
  #  return True
  return False

def update(list, hash, member, old):
  data = build_data(member)
  om = old['merge_fields']
  if has_changed(old, data) == False:
    if member['Email'] != '':
      print('no change to ', member['Email'])
    else:
      print('no change to member with GOLD ID', member['ID'])
    return
  data['status_if_new'] = 'subscribed'
  try:
    client.lists.set_list_member(list, hash, data)
    print('updated', member['Email'])
  except ApiClientError as error:
    print("Error: {}".format(error.text))
    print("%s\t%s" % (id, member['Lastname']))

def simple_upsert(list, email, member):
  hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
  try:
    response = client.lists.get_list_member(list, hash)
    if response['status'] == 'archived':
      print('was archived')
      add(list, email, member)
    else:
      update(list, hash, member, response)
  except ApiClientError as error:
    add(list, email, member)

def archive(list, email):
  hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
  try:
    r = client.lists.delete_list_member(list, hash)
    print('archive', email, r)
  except ApiClientError as error:
    pass

def archive_member(list, member):
  email = member['Email']
  dummy = member['ID']+'@oga.org.uk'
  if email == '':
    archive(list, dummy)
  else:
    archive(list, email)

def upsert(list, member):
  email = member['Email']
  dummy = member['ID']+'@oga.org.uk'
  if email == '':
    simple_upsert(list, dummy, member)
  else:
    simple_upsert(list, email, member)
    archive(list, dummy) # member might have given us an email

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
  response = client.lists.get_list_interest_categories(list)
  for category in response['categories']:
    print('collecting', category['title'])
    response = client.lists.list_interest_category_interests(list, category['id'])
    group = {}
    for interest in response['interests']:
      group[interest['name']] = interest['id']
    audience_data[category['title']] = group
except ApiClientError as error:
  print("Error: {}".format(error.text))

with open(sys.argv[1], newline='') as csvfile:
  members = csv.DictReader(csvfile)
  memberships = {}
  for member in members:
    if member['Area'] not in excludes:
      if member['Status'] == 'Left OGA':
        archive_member(list, member)
      else:
        number = member['Member Number']
        if number in memberships:
          memberships[number].append(member)
        else:
          memberships[number] = [member]
  for number in memberships:
    membership = memberships[number]
    if len(membership) == 1:
      upsert(list, membership[0])
    else:
      emails = {}
      for member in membership:
        emails[member['Email'].lower()] = True
      if len(emails) == len(membership):
        for member in membership:
          upsert(list, member)
      else:
        for member in membership:
          if member['Primary'] == 'false':
            member['Email'] = ''
          upsert(list, member)
