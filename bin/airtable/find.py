import os
import sys
from pyairtable import Table
from pyairtable.formulas import match
from util import table_id

api_key = os.environ["AIRTABLE_API_KEY"]
member_number = int(sys.argv[1])
table = Table(api_key, table_id(member_number), 'Members')
t = table.all(formula=match({"Member Number": member_number}))
for member in t:
    print(member)
