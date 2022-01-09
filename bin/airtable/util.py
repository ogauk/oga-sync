import os
split = int(os.environ["AIRTABLE_SPLIT"])

def table_id(member_number):
  if member_number <= split:
    return os.environ["AIRTABLE_LOWER"]
  else:
    return os.environ["AIRTABLE_UPPER"]

int_fields = ['ID', 'Member Number', 'Edited By:', 'Year Joined', 'Year Of Birth']
bool_fields = ['GDPR', 'Primary', 'Trailer']

def convert(record):
 result = {}
 for key in record.keys():
    if key in int_fields:
      if record[key].strip() != '':
        result[key] = int(record[key])
    elif key in bool_fields:
      if record[key]=='true':
        result[key]=True
    elif record[key] != '':
      val = record[key].replace('\r', '').replace(' \n', '\n').rstrip(' ')
      if val != '':
        result[key] = val
 return result
