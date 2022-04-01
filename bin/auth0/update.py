import requests
import sys
import csv
import json

headers = { 'authorization': "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJEVkZNVEEwTXpjeFJrVTBOekExT0VSQ01VTTVRelk0TlRVMlJESkRPRFUxUlRVeVFrVkNOQSJ9.eyJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLWFsbG93ZWQtcm9sZXMiOlsiZWRpdG9yIl0sIngtaGFzdXJhLWRlZmF1bHQtcm9sZSI6ImVkaXRvciJ9LCJodHRwczovL29nYS5vcmcudWsvcm9sZXMiOlsiZWRpdG9yIl0sImlzcyI6Imh0dHBzOi8vZGV2LXVmODdlOTQyLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJrRUw2MTVDVzFCUzZiWklER04xRnRqWk1CcXpaNDQ3S0BjbGllbnRzIiwiYXVkIjoiaHR0cHM6Ly9kZXYtdWY4N2U5NDIuZXUuYXV0aDAuY29tL2FwaS92Mi8iLCJpYXQiOjE2NDg4Mjc0MTEsImV4cCI6MTY0ODkxMzgxMSwiYXpwIjoia0VMNjE1Q1cxQlM2YlpJREdOMUZ0alpNQnF6WjQ0N0siLCJzY29wZSI6InJlYWQ6Y2xpZW50X2dyYW50cyBjcmVhdGU6Y2xpZW50X2dyYW50cyBkZWxldGU6Y2xpZW50X2dyYW50cyB1cGRhdGU6Y2xpZW50X2dyYW50cyByZWFkOnVzZXJzIHVwZGF0ZTp1c2VycyBkZWxldGU6dXNlcnMgY3JlYXRlOnVzZXJzIHJlYWQ6dXNlcnNfYXBwX21ldGFkYXRhIHVwZGF0ZTp1c2Vyc19hcHBfbWV0YWRhdGEgZGVsZXRlOnVzZXJzX2FwcF9tZXRhZGF0YSBjcmVhdGU6dXNlcnNfYXBwX21ldGFkYXRhIHJlYWQ6dXNlcl9jdXN0b21fYmxvY2tzIGNyZWF0ZTp1c2VyX2N1c3RvbV9ibG9ja3MgZGVsZXRlOnVzZXJfY3VzdG9tX2Jsb2NrcyBjcmVhdGU6dXNlcl90aWNrZXRzIHJlYWQ6Y2xpZW50cyB1cGRhdGU6Y2xpZW50cyBkZWxldGU6Y2xpZW50cyBjcmVhdGU6Y2xpZW50cyByZWFkOmNsaWVudF9rZXlzIHVwZGF0ZTpjbGllbnRfa2V5cyBkZWxldGU6Y2xpZW50X2tleXMgY3JlYXRlOmNsaWVudF9rZXlzIHJlYWQ6Y29ubmVjdGlvbnMgdXBkYXRlOmNvbm5lY3Rpb25zIGRlbGV0ZTpjb25uZWN0aW9ucyBjcmVhdGU6Y29ubmVjdGlvbnMgcmVhZDpyZXNvdXJjZV9zZXJ2ZXJzIHVwZGF0ZTpyZXNvdXJjZV9zZXJ2ZXJzIGRlbGV0ZTpyZXNvdXJjZV9zZXJ2ZXJzIGNyZWF0ZTpyZXNvdXJjZV9zZXJ2ZXJzIHJlYWQ6ZGV2aWNlX2NyZWRlbnRpYWxzIHVwZGF0ZTpkZXZpY2VfY3JlZGVudGlhbHMgZGVsZXRlOmRldmljZV9jcmVkZW50aWFscyBjcmVhdGU6ZGV2aWNlX2NyZWRlbnRpYWxzIHJlYWQ6cnVsZXMgdXBkYXRlOnJ1bGVzIGRlbGV0ZTpydWxlcyBjcmVhdGU6cnVsZXMgcmVhZDpydWxlc19jb25maWdzIHVwZGF0ZTpydWxlc19jb25maWdzIGRlbGV0ZTpydWxlc19jb25maWdzIHJlYWQ6aG9va3MgdXBkYXRlOmhvb2tzIGRlbGV0ZTpob29rcyBjcmVhdGU6aG9va3MgcmVhZDphY3Rpb25zIHVwZGF0ZTphY3Rpb25zIGRlbGV0ZTphY3Rpb25zIGNyZWF0ZTphY3Rpb25zIHJlYWQ6ZW1haWxfcHJvdmlkZXIgdXBkYXRlOmVtYWlsX3Byb3ZpZGVyIGRlbGV0ZTplbWFpbF9wcm92aWRlciBjcmVhdGU6ZW1haWxfcHJvdmlkZXIgYmxhY2tsaXN0OnRva2VucyByZWFkOnN0YXRzIHJlYWQ6aW5zaWdodHMgcmVhZDp0ZW5hbnRfc2V0dGluZ3MgdXBkYXRlOnRlbmFudF9zZXR0aW5ncyByZWFkOmxvZ3MgcmVhZDpsb2dzX3VzZXJzIHJlYWQ6c2hpZWxkcyBjcmVhdGU6c2hpZWxkcyB1cGRhdGU6c2hpZWxkcyBkZWxldGU6c2hpZWxkcyByZWFkOmFub21hbHlfYmxvY2tzIGRlbGV0ZTphbm9tYWx5X2Jsb2NrcyB1cGRhdGU6dHJpZ2dlcnMgcmVhZDp0cmlnZ2VycyByZWFkOmdyYW50cyBkZWxldGU6Z3JhbnRzIHJlYWQ6Z3VhcmRpYW5fZmFjdG9ycyB1cGRhdGU6Z3VhcmRpYW5fZmFjdG9ycyByZWFkOmd1YXJkaWFuX2Vucm9sbG1lbnRzIGRlbGV0ZTpndWFyZGlhbl9lbnJvbGxtZW50cyBjcmVhdGU6Z3VhcmRpYW5fZW5yb2xsbWVudF90aWNrZXRzIHJlYWQ6dXNlcl9pZHBfdG9rZW5zIGNyZWF0ZTpwYXNzd29yZHNfY2hlY2tpbmdfam9iIGRlbGV0ZTpwYXNzd29yZHNfY2hlY2tpbmdfam9iIHJlYWQ6Y3VzdG9tX2RvbWFpbnMgZGVsZXRlOmN1c3RvbV9kb21haW5zIGNyZWF0ZTpjdXN0b21fZG9tYWlucyB1cGRhdGU6Y3VzdG9tX2RvbWFpbnMgcmVhZDplbWFpbF90ZW1wbGF0ZXMgY3JlYXRlOmVtYWlsX3RlbXBsYXRlcyB1cGRhdGU6ZW1haWxfdGVtcGxhdGVzIHJlYWQ6bWZhX3BvbGljaWVzIHVwZGF0ZTptZmFfcG9saWNpZXMgcmVhZDpyb2xlcyBjcmVhdGU6cm9sZXMgZGVsZXRlOnJvbGVzIHVwZGF0ZTpyb2xlcyByZWFkOnByb21wdHMgdXBkYXRlOnByb21wdHMgcmVhZDpicmFuZGluZyB1cGRhdGU6YnJhbmRpbmcgZGVsZXRlOmJyYW5kaW5nIHJlYWQ6bG9nX3N0cmVhbXMgY3JlYXRlOmxvZ19zdHJlYW1zIGRlbGV0ZTpsb2dfc3RyZWFtcyB1cGRhdGU6bG9nX3N0cmVhbXMgY3JlYXRlOnNpZ25pbmdfa2V5cyByZWFkOnNpZ25pbmdfa2V5cyB1cGRhdGU6c2lnbmluZ19rZXlzIHJlYWQ6bGltaXRzIHVwZGF0ZTpsaW1pdHMgY3JlYXRlOnJvbGVfbWVtYmVycyByZWFkOnJvbGVfbWVtYmVycyBkZWxldGU6cm9sZV9tZW1iZXJzIHJlYWQ6ZW50aXRsZW1lbnRzIHJlYWQ6YXR0YWNrX3Byb3RlY3Rpb24gdXBkYXRlOmF0dGFja19wcm90ZWN0aW9uIHJlYWQ6b3JnYW5pemF0aW9ucyB1cGRhdGU6b3JnYW5pemF0aW9ucyBjcmVhdGU6b3JnYW5pemF0aW9ucyBkZWxldGU6b3JnYW5pemF0aW9ucyBjcmVhdGU6b3JnYW5pemF0aW9uX21lbWJlcnMgcmVhZDpvcmdhbml6YXRpb25fbWVtYmVycyBkZWxldGU6b3JnYW5pemF0aW9uX21lbWJlcnMgY3JlYXRlOm9yZ2FuaXphdGlvbl9jb25uZWN0aW9ucyByZWFkOm9yZ2FuaXphdGlvbl9jb25uZWN0aW9ucyB1cGRhdGU6b3JnYW5pemF0aW9uX2Nvbm5lY3Rpb25zIGRlbGV0ZTpvcmdhbml6YXRpb25fY29ubmVjdGlvbnMgY3JlYXRlOm9yZ2FuaXphdGlvbl9tZW1iZXJfcm9sZXMgcmVhZDpvcmdhbml6YXRpb25fbWVtYmVyX3JvbGVzIGRlbGV0ZTpvcmdhbml6YXRpb25fbWVtYmVyX3JvbGVzIGNyZWF0ZTpvcmdhbml6YXRpb25faW52aXRhdGlvbnMgcmVhZDpvcmdhbml6YXRpb25faW52aXRhdGlvbnMgZGVsZXRlOm9yZ2FuaXphdGlvbl9pbnZpdGF0aW9ucyIsImd0eSI6ImNsaWVudC1jcmVkZW50aWFscyJ9.qjPRQ_K3dnxboeIhBrKi03_xX1MVlGQSDjpiedL2dSJduNrtNvDv1aNIVboBDhOauzjQXtUOf4IzMfCLrh8F42ixBE6q23euBIpWi_dJRqT_RpFgqJ76bQRZL4Sd8dmif_aH_acOgLLlGp7f_KPAHcVYTTnJ0RYaPMYyOPLQc7V6_A58bxyZmLl4T4x70lXCAGwHb0gG2l8RO_GEnL1lfg4IpV-6F26d24WGhT5Qu6yRt2B95qPuGovT2Mq-UlHCYQTbLnCxZyiuxek5ys8uOdA32j5xoThE3bcslZqtGI11FUkajvljYjkPNBQsbhnfv6WyZxB1tYvwUb0e7YZJ0Q" }

def getMemberRole():
  r = requests.get('https://dev-uf87e942.eu.auth0.com/api/v2/roles', headers=headers)
  roles = r.json()
  users = []
  for role in roles:
    if role['name'] == 'member':
      return role['id']

member_role_id = getMemberRole()

def update(member, auth0):
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
        url = f"https://dev-uf87e942.eu.auth0.com/api/v2/users/{auth0['user_id']}"
        r = requests.patch(url, headers=headers, json=patch)
        #print(r.json())
    print(member['Status'], member['Firstname'], member['Lastname'])
    if member['Status'] != 'Left OGA':
        url = f"https://dev-uf87e942.eu.auth0.com/api/v2/users/{auth0['user_id']}/roles"
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
    url = f"https://dev-uf87e942.eu.auth0.com/api/v2/users?q=given_name:{given_name} AND family_name:{family_name}"
    r = requests.get(url, headers=headers)
    a0 = r.json()
    print(a0)
    if len(a0) > 0:
        update(member, a0[0])

def getUsersWithRole(role_id):
  r = requests.get(f"https://dev-uf87e942.eu.auth0.com/api/v2/roles/{role_id}/users", headers=headers, params={'take': 60})
  data = r.json()
  while 'next' in data:
    users.extend(data['users'])
    r = requests.get(f"https://dev-uf87e942.eu.auth0.com/api/v2/roles/{role_id}/users", headers=headers, params={'take': 60, 'from': data['next']})
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
          f"https://dev-uf87e942.eu.auth0.com/api/v2/users?q=email:{email}",
          # f"https://dev-uf87e942.eu.auth0.com/api/v2/users-by-email?email={email}",
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
