import os
import sys
import csv
import hashlib
import json
import iso3166
import difflib
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
from geopy.geocoders import Nominatim
import googlemaps

excludes = {}
if  'EXCLUDE' in os.environ:
  excludes = json.loads(os.environ.get('EXCLUDE'))

gmaps = googlemaps.Client(key=os.environ['GOOGLE_API_KEY'])
geolocator = Nominatim(user_agent="ogasync")

def country(member):
  if member['Country'] == '':
    r = 'GB'
  elif member['Country'] == 'United Kingdom':
    r = 'GB'
  elif member['Country'] == 'Eire':
    r = 'IE'
  elif len(member['Country']) == 2:
    r = iso3166.countries_by_alpha2[member['Country'].upper()].alpha2
  elif len(member['Country']) == 3:
    r = iso3166.countries_by_alpha3[member['Country'].upper()].alpha2
  else:
    n = member['Country'].upper()
    if n in iso3166.countries_by_name:
      r = iso3166.countries_by_name[n].alpha2
    else:
      rr = difflib.get_close_matches(n, iso3166.countries_by_name, 5)
      n0 = n.split(' ')[0].rstrip('S')
      r = 'GB'
      for s in rr:
        if n0 in s:
          r = iso3166.countries_by_name[s].alpha2
  return r

def tidy(s):
  return ' '.join([x for x in s.split(' ') if x != ''])

def address(member):
  addr1 = tidy(member['Address1'])
  if member['Address2'] != '':
    addr1 = addr1 + ', ' + tidy(member['Address2'])
  r = { 'addr1': addr1, 'city': tidy(member['Town']), 'state': tidy(member['County']), 'zip': tidy(member['Postcode']) }
  if member['Address3'] == '':
    r['addr2'] = ''
  else:
    r['addr2'] = tidy(member['Address3'])
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
  elif member['County'] == '' and member['Country'] == 'Australia':
    x = member['Postcode'].split(' ')
    if len(x)==2:
      r['state'] = x[0]
      r['zip'] = x[1]
  elif member['Postcode'] == '' and member['Country'] == 'Netherlands':
    if member['Address3'].strip() != '':
      r['zip'] = member['Address3'].strip()
    elif member['Address2'].strip() != '':
      r['zip'] = member['Address2'].strip()
  elif member['Postcode'] == '' and member['Country'] == 'Eire':
    t = member['Town'].split(' ')
    if len(t) == 2 and t[0] == 'Dublin' and t[1].isnumeric():
      district = int(t[1])
      r['zip'] = f"D{district:02d}"
    else:
      pass
  r['country'] = country(member)
  return r

def address1(member):
  r = []
  r.append(tidy(member['Address1']))
  r.append(tidy(member['Address2']))
  r.append(tidy(member['Address3']))
  r.append(tidy(member['Town']))
  r.append(tidy(member['County']))
  r.append(tidy(member['Postcode']))
  r.append(country(member))
  return ', '.join([word for word in r if word != ''])

def addAddress(merge_fields, member):
  addr = address(member)
  if addr['addr1'] != '' and addr['city'] != '' and addr['zip'] != '':
    merge_fields['ADDRESS'] = addr
  else:
    a = address1(member)
    print('trying to geolocate', a)
    location = geolocator.geocode(a)
    if location is None:
      print('no location found, try Google')
      geocode_result = gmaps.geocode(a)
      glocation = geocode_result[0]['geometry']['location']
      if glocation is None:
        merge_fields['ADDRESS'] = a
        return
      coords = f"{glocation['lat']}, {glocation['lng']}"
    coords = f"{location.latitude}, {location.longitude}"
    print('coords', coords)
    location = geolocator.reverse(coords)
    if 'address' in location.raw and 'postcode' in location.raw['address']:
      postcode = location.raw['address']['postcode']
      member['Postcode'] = postcode
      addr = address(member)
      merge_fields['ADDRESS'] = addr
      print(f"member {member['ID']} {member['Email']} might have postcode {postcode}")
    else:
      print('no postcode found')
      merge_fields['ADDRESS'] = a

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
  global audience_data
  global list
  payment_methods = audience_data['Payment Method']
  payment_method = member['Payment Method']
  if payment_method == None or payment_method == '':
    payment_method = 'PayPal'
  if payment_method not in payment_methods.keys():
    print('missing payment method', payment_method)
    print(payment_methods)
    category_id = audience_data['categories']['Payment Method']
    print(category_id)
    r = client.lists.create_interest_category_interest(list, category_id, {'name': payment_method})
    print(r)
    print('re-fetching audience data')
    audience_data = get_audience_data(list)
    payment_methods = audience_data['Payment Method']
  try:
    interests[payment_methods[member['Payment Method']]] = True
  except KeyError as error:
    print(error)
    print(member)

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

def search(list, query):
  result = []
  try:
    response = client.searchMembers.search(query, list_id=list)
    r = response['full_search']
    return r['members']
  except ApiClientError as error:
    try:
      e = json.loads(error.text)
      print(f'{e["title"]} searching for {query}')
    except:
      print(error)
  return result

def mc_key(email):
  return hashlib.md5(email.lower().strip().encode('utf-8')).hexdigest()

def entries_for_member(list, member):
  r = []
  matches = search(list, f'{member["Firstname"]} {member["Lastname"]}')
  id = int(member['ID'])
  for match in matches:
    match_id = match['merge_fields']['GOLD']
    if match_id == id:
      r.append(match)
  return r

def delete(list, email):
  try:
    r = client.lists.delete_list_member(list, mc_key(email))
    print('archived', email)
  except ApiClientError as error:
    e = json.loads(error.text)
    print(f'{e["title"]} deleting {email}')

def delete_old_email(list, email, member):
  matches = entries_for_member(list, member)
  if len(matches)>1:
    for match in matches:
      match_email = match['email_address']
      if match_email != email:
        delete(list, match_email)

def add(list, email, member):
  data = build_data(member)
  data['email_address'] = email
  try:
    response = client.lists.add_list_member(list, data)
    print('added', email)
  except ApiClientError as error:
    e = json.loads(error.text)
    if e['title'] == 'Invalid Resource':
      e = json.loads(error.text)
      print(f'{e["title"]} adding {member["ID"]} {member["Lastname"]} {email}')
      try:
        address = data['merge_fields']['ADDRESS']
        del data['merge_fields']['ADDRESS']
        response = client.lists.add_list_member(list, data)
        print(f'added {member["Email"]} omitting invalid address {address}')
      except ApiClientError as error:
        e = json.loads(error.text)
        print(f'{e["title"]} adding {member["ID"]} {member["Lastname"]} {email}')
        return
    elif e['title'] == 'Resource Not Found':
      print(f'{e["title"]} for {member["ID"]} {member["Lastname"]}')
    else:
      e = json.loads(error.text)
      print(f'{e["title"]} adding {member["ID"]} {member["Lastname"]} {email}')

def same(old, new):
  for key in new:
    if old[key] != new[key]:
        return False, { 'key': key, 'old': old[key], 'new': new[key] }
  for key in old:
    if old[key] != new[key]:
        return False, { 'key': key, 'old': old[key], 'new': new[key] }
  return True, None

def same_interests(complete, partial):
  for key in complete:
    if key in partial:
      if complete[key] != partial[key]:
        return False, { 'key': key, 'complete': complete, 'partial': partial }
    elif complete[key]:
      partial[key] = False
      return False, key
    else:
      pass
  return True, None

def same_permissions(old, new):
  for p in old:
    for q in new:
      if p['marketing_permission_id'] == q['marketing_permission_id']:
        if p['enabled'] != q['enabled']:
          return False, { 'old': old, 'new': new }
  return True, None

def has_changed(old, new):
  s, d = same(old['merge_fields'], new['merge_fields'])
  if s == False:
    return True, d
  s, d = same_interests(old['interests'], new['interests'])
  if s == False:
    return True, d
  #if same_permissions(old['marketing_permissions'], new['marketing_permissions']) == False:
  #  print(old['marketing_permissions'])
  #  print(new['marketing_permissions'])
  #  return True
  return False, None

def update(list, email, member, data, changes):
  hash = mc_key(email)
  data['status_if_new'] = 'subscribed'
  try:
    client.lists.set_list_member(list, hash, data)
    if '@oga.org.uk' in email:
      print(f'updated member with GOLD ID {member["ID"]} with changes {changes}')
    else:
      print(f'updated {email} with changes {changes}')
  except ApiClientError as error:
    e = json.loads(error.text)
    if e['title'] == 'Invalid Resource':
      try:
        address = data['merge_fields']['ADDRESS']
        del data['merge_fields']['ADDRESS']
        client.lists.set_list_member(list, hash, data)
        print(f'updated {member["Email"]} omitting invalid address {address}')
      except ApiClientError as error:
        e = json.loads(error.text)
        print(f'{e["title"]} for {member["ID"]} {member["Lastname"]}')
    elif e['title'] == 'Resource Not Found':
      print(f'{e["title"]} for {member["ID"]} {member["Lastname"]}')
    else:
      print(f'{e["title"]} for {member["ID"]} {member["Lastname"]}')

def update_if_changed(list, email, member, old):
  data = build_data(member)
  changed, changes = has_changed(old, data)
  if changed:
    update(list, email, member, data, changes)
  else:
    if '@oga.org.uk' in email:
      print('no change to member with GOLD ID', member['ID'])
    else:
      print('no change to', email)

def crud(list, member):
  email = member['Email']
  try:
    response = client.lists.get_list_member(list, mc_key(email))
  except ApiClientError as error:
    response = { 'status': 'missing' }
  if response['status'] in ['missing', 'archived']:
    if member['Status'] == 'Left OGA':
      print('no change to ex member', email)
    else:
      add(list, email, member)
  else:
    if member['Status'] == 'Left OGA':
      delete(list, email)
      print(f'archive {email}')
    else:
      update_if_changed(list, email, member, response)
  delete_old_email(list, email, member)

def getlistid(name):
  r = client.lists.get_all_lists()
  for l in r['lists']:
    if l['name'] == name:
      return l['id']

def get_audience_data(list):
  audience_data = {}
  try:
    response = client.lists.get_list_interest_categories(list)
    audience_data['categories'] = {}
    for category in response['categories']:
      print('collecting', category['title'])
      audience_data['categories'][category['title']] = category['id']
      try:
        response = client.lists.list_interest_category_interests(list, category['id'])
        group = {}
        for interest in response['interests']:
          group[interest['name']] = interest['id']
        audience_data[category['title']] = group
      except ApiClientError as error:
        e = json.loads(error.text)
        print(f'{e["title"]} getting category {interest["name"]}')
  except ApiClientError as error:
    e = json.loads(error.text)
    print(f'{e["title"]} getting categories')
  return audience_data

client = MailchimpMarketing.Client()

client.set_config({
  "api_key": os.environ.get('MAILCHIMP_API_KEY'),
  "server": os.environ.get('MAILCHIMP_SERVER')
})

list = getlistid(os.environ.get('AUDIENCE'))

audience_data = get_audience_data(list)

with open(sys.argv[1], newline='') as csvfile:
  members = csv.DictReader(csvfile)
  # group families together
  memberships = {}
  for member in members:
    if member['Area'] not in excludes:
      if '@' in member['Email']:
        member['Email in GOLD'] = member['Email']
        member['Email'] = member['Email'].lower().strip()
      else:
        member['Email'] = member['ID']+'@oga.org.uk'
      number = member['Member Number']
      if number in memberships:
        memberships[number].append(member)
      else:
        memberships[number] = [member]
  # make emails unique within a family
  for number in memberships:
    membership = memberships[number]
    if len(membership) > 1:
      emails = {}
      for member in membership:
        emails[member['Email']] = True
      if len(emails) < len(membership):
        usedEmail = False
        for member in membership:
          if usedEmail:
            member['Email'] = member['ID']+'@oga.org.uk'
          elif member['Primary'] == 'false':
            member['Email'] = member['ID']+'@oga.org.uk'
          else:
            usedEmail = True
  # update
  for number in memberships:
    membership = memberships[number]
    for member in membership:
      crud(list, member)
