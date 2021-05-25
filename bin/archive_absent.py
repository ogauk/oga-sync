import os
import sys
import csv
import hashlib
import json
import iso3166
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

with open(sys.argv[1], newline='') as csvfile:
  members = csv.DictReader(csvfile)
  gold = {}
  gold_full = {}
  for member in members:
    id = int(member['ID'])
    gold[id] = member['Email'].strip().lower()
    gold_full[id] = member

  
with open('noaddr.csv', 'w', newline='') as csvfile:
  writer = csv.DictWriter(csvfile, fieldnames=members.fieldnames)
  writer.writeheader()
  for i in range(0, 2):
    response = client.lists.get_list_members_info(list, fields=['members.id','members.merge_fields', 'members.email_address'], offset=1000*i, count=1000)
    mc_members = response['members']
    for r in mc_members:
      mf = r['merge_fields']
      gold_id = mf['GOLD']
      email = r['email_address']
      if gold_id in gold:
        if mf['ADDRESS'] == '':
          print(mf['GOLD'], mf['FNAME'], mf['LNAME'], mf['MEMBER'], gold_full[gold_id]['Country'])
          writer.writerow(gold_full[gold_id])
        if email.lower() == gold[gold_id]:
          pass
        elif email == f'{gold_id}@oga.org.uk'
          if  gold[gold_id] == '':
            pass
          else:
            pass
        else:
          print(gold_id, email, gold[gold_id])
          hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
          try:
            r = client.lists.delete_list_member(list, hash)
            print('archive', email)
          except ApiClientError as error:
            print('===')
            print("Error: {}".format(error.text))
            print(gold_id, email, gold[gold_id])
            print('===')
            e = json.loads(error.text)
      else:
          print(gold_id, email, 'not in GOLD')
