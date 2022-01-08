#!/usr/bin/env python3

import sys
import os
import csv
from pysqlcipher3 import dbapi2 as sqlite
conn = sqlite.connect('gold.db')
cur = conn.cursor()
cur.execute(f"PRAGMA key='{os.environ['SPASS']}'")
with open(sys.argv[1], newline='') as csvfile:
  members = csv.DictReader(csvfile)
  dict = dict(list(members)[0])
  fields = "'" + "' text, '".join(dict.keys()) + "' text"
  print(fields)
  cur.execute(f"create table gold ({fields})")
conn.commit()
cur.close()
