import requests
import sys
import csv
import json
import http.client
import os

auth0_domain = os.environ['AUTH0_DOMAIN']

conn = http.client.HTTPSConnection(auth0_domain)

payload = {
  "client_id": os.environ['AUTH0_CLIENT_ID'],
  "client_secret": os.environ['AUTH0_CLIENT_SECRET'],
  "audience": f"https://{auth0_domain}/api/v2/",
  "grant_type": "client_credentials"
}

headers = { 'content-type': "application/json" }

#r = requests.post(f"https://{auth0_domain}/oath/token", json=payload, headers=headers)
#print(r.json)
conn.request("POST", "/oauth/token", json.dumps(payload), headers)
res = conn.getresponse()
data = res.read()
token = json.loads(data.decode("utf-8"))
access_token = token['access_token']

headers = { 'authorization': f"Bearer {access_token}" }

def getMemberRole():
  r = requests.get(f"https://{auth0_domain}/api/v2/roles", headers=headers)
  if not r.ok:
    print(r)
    return None
  roles = r.json()
  users = []
  for role in roles:
    if role['name'] == 'member':
      return role['id']

member_role_id = getMemberRole()

def update(member, auth0):
    base_url = f"https://{auth0_domain}/api/v2/users"
    print('checking for update', member['Email'])
    patch = {}
    if 'app_metadata' in auth0:
        aw = False
        am = auth0['app_metadata']
        print(am)
        if 'id' in am:
            id = am['id']
            if id != int(member['ID']):
                aw = True
        else:
            aw = True
        if 'member' in am:
            mn = am['member']
            if mn != int(member['Member Number']):
                aw = True
        else:
            aw = True
    else:
        aw = True
    if aw:
        patch['app_metadata'] = { 'id': int(member['ID']), 'member': int(member['Member Number']) }
    if auth0['user_id'].startswith('auth0'):
        n = f"{member['Firstname']} {member['Lastname']}"
        if 'name' in auth0:
            if auth0['name'] != n:
                patch['name'] = n
        else:
            patch['name'] = n
        if 'family_name' in auth0:
            if auth0['family_name'] != member['Lastname']:
                patch['family_name'] = member['Lastname']
        else:
            patch['family_name'] = member['Lastname']
        if 'given_name' in auth0:
            if auth0['given_name'] != member['Firstname']:
                patch['given_name'] = member['Firstname']
        else:
            patch['given_name'] = member['Firstname']
    if patch:
        print(f"patching {auth0['user_id']} with {patch}")
        url = f"{base_url}/{auth0['user_id']}"
        r = requests.patch(url, headers=headers, json=patch)
        #print(r.json())
    print(member['Status'], member['Firstname'], member['Lastname'])
    if member['Status'] != 'Left OGA':
        url = f"{base_url}/{auth0['user_id']}/roles"
        r = requests.get(url, headers=headers)
        roles = set([ro['id'] for ro in r.json()])
        if member_role_id not in roles:
            roles.add(member_role_id)
            print(list(roles))
            r = requests.post(url, headers=headers, json={ 'roles': list(roles) })
            print(r)

def checkByName(member):
    given_name = member['Firstname']
    family_name = member['Lastname'].replace('-', '*')
    if given_name.strip() == '' or family_name.strip() == '':
      return
    url = f"https://{auth0_domain}/api/v2/users?q=given_name:{given_name} AND family_name:{family_name}"
    r = requests.get(url, headers=headers)
    a0 = r.json()
    print(a0)
    if len(a0) > 0:
        update(member, a0[0])

def getUsersWithRole(role_id):
  r = requests.get(f"https://{auth0_domain}/api/v2/roles/{role_id}/users", headers=headers, params={'take': 60})
  data = r.json()
  while 'next' in data:
    users.extend(data['users'])
    r = requests.get(f"https://{auth0_domain}/api/v2/roles/{role_id}/users", headers=headers, params={'take': 60, 'from': data['next']})
    data = r.json()
  users.extend(data['users'])
  print(len(users))
  return users

members = []
with open(sys.argv[1], newline='') as csvfile:
    m = csv.DictReader(csvfile)
    for member in m:
        members.append(member)
for member in members:
    email = member['Email']
    if '@' in email:
        r = requests.get(
          f"https://{auth0_domain}/api/v2/users?q=email:{email}",
          # f"https://{auth0_domain}/api/v2/users-by-email?email={email}",
          headers=headers
        )
        a0 = r.json()
        if len(a0) == 0:
            pass
            #checkByName(member)
        else:
            update(member, a0[0])
    else:
        pass
        #checkByName(member)
