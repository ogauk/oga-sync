#!/usr/bin/env python3
import sys
import os
import csv
from pysqlcipher3 import dbapi2 as sqlite
from io import StringIO
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

conn = sqlite.connect('gold.db')
cur = conn.cursor()
cur.execute(f"PRAGMA key='{os.environ['SPASS']}'")
cur.execute('delete from gold')
conn.commit()
cur.close()
cur = conn.cursor()
with open(sys.argv[1], newline='') as csvfile:
  members = csv.DictReader(csvfile)
  for member in members:
    values = '", "'.join([strip_tags(s).replace('"', '') for s in member.values()])
    print(values)
    cur.execute(f'insert into gold values ("{values}")')
conn.commit()
cur.close()
