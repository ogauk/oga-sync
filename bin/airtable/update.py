import csv
import os
import sys
from pyairtable import Table
from pyairtable.formulas import match
from util import table_id, convert

api_key = os.environ["AIRTABLE_API_KEY"]

def show_diff(existing, incoming):
  for key in existing.keys():
    if key not in incoming:
      print(f"{key} missing from incoming {existing[key]}")
    elif existing[key] != incoming[key]:
      old = existing[key]
      inc = incoming[key]
      print(f"{key} differs airtable: '{old}' GOLD: '{inc}'")
      for i in range(len(inc)):
        if i<len(old):
          print(f"{repr(inc[i])} {repr(old[i])}")
        else:
          print(f"{repr(inc[i])}")

def update(members):
    try:
      member_number = int(members[0]['Member Number'])
    except:
      return
    table = Table(api_key, table_id(member_number), 'Members')
    t = table.all()
    existing_by_id = {m['fields']['ID']: m for m in t}
    for member in members:
      id = int(member['ID'])
      converted = convert(member)
      try:
        if id in existing_by_id:
          existing = existing_by_id[id]['fields']
          if existing == converted:
              pass
              #print('no change for ', id)
          else:
              print(id, 'needs update')
              #show_diff(existing, converted)
              r = table.update(existing_by_id[id]['id'], converted)
              print(r)
        else:
          print('new', member['ID'])
          table.create(converted)
      except Exception as e:
          print(type(e))
          print(e.args)
          print(converted)

if __name__ == "__main__":
    with open(sys.argv[1], newline='') as csvfile:
        members = csv.DictReader(csvfile)
        update(list(members))
