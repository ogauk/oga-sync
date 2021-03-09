# oga-sync
Sync GOLD and other systems

This repository contains code to sync data between OGA systems.

It is currently configured to run in Heroku but can operate on any Unix-like system (linux, BSD, MacOS, etc.)

## Mailchimp

Currently the only synchronisation is a one-way sync from GOLD (aka 'new GOLD') to MailChimp.

The bin/sync shell script runs once per day and

1. does a full export of the members from GOLD as a comma separated values file
1. updates Mailchimp with changed, added or deleted records
1. tidies up by deleting the csv file and the GOLD session cookie

The scripts use environment variables to configure the operation:

- USER is the GOLD username of a user with at least read access to the members table
- PASS is the password of that user

- MAILCHIMP_API_KEY is an API key with admin access to the required Mailchimp account
- MAILCHIMP_SERVER is the server listed in the API key in Mailchimp (e.g. us1)

- AUDIENCE is the name of the Audience (called list in the api documentation)
- EXCLUDE is a list of OGA Areas to exclude from the synchronisation. This is mostly to reduce the number of records during testing.

The exclude list is a JSON array. For example:

["East Coast", "Solent", "South West"]

## Other scripts

In addition there are python scripts to create the list, audiences and segments. These are intended to be run manually.

## Dependencies

- The member list is fetched using curl.
- The update function is a python script requiring at least python 3.6
- The update function uses the Mailchimp sdk as listed in the requirements.txt file.

