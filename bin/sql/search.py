#!/usr/bin/env python3
import os
import sys
from pysqlcipher3 import dbapi2 as sqlite

conn = sqlite.connect('gold.db')
cur = conn.cursor()
cur.execute(f"PRAGMA key='{os.environ['SPASS']}'")
cur.execute("SELECT name FROM PRAGMA_TABLE_INFO('gold')")
cols = cur.fetchall()
print(f"'{sys.argv[1]}'")
cur.execute(f"SELECT * FROM gold WHERE \"Member Number\" = '{sys.argv[1]}'")
rows = cur.fetchall()

members = list()
for row in rows:
    member = dict()
    for i in range((len(row))):
        member[cols[i][0]] = row[i]
    members.append(member)
cur.close()
print(members)
print(f"read {len(members)} members")
