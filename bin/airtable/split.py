import os
import sys
import csv
import json

def write(filename, data):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        writer.writeheader()
        for member in data:
            writer.writerow(member)

with open(sys.argv[1], newline='') as csvfile:
    members = csv.DictReader(csvfile)
    lower = []
    upper = []
    split = int(os.environ["AIRTABLE_SPLIT"])
    total = 0
    for member in members:
      total = total + 1
      id = int(member['Member Number'])
      if id < split:
          lower.append(member)
      else:
          upper.append(member)
    print(f"total {total} lower {len(lower)} upper {len(upper)} check {total==(len(lower)+len(upper))}")
    if len(lower) > 0:
        write(sys.argv[2], lower)
    if len(upper) > 0:
        write(sys.argv[3], upper)
