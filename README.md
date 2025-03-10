# Cine2cal

Scrape Cinemateket web site for movies and create events in Google calendar.

Written by David Hendén (km@grogg.org).


## Files

* cine2cal.py - Main script
* cinemateket.py - Module for scraping Cinematekets web site
* dcal.py - Module for handling Google Calendar events
* testcal.py - Script to extract calendar events

You also need a google API key file: client_secret.json


## Modules

You need to install some modules:

### Windows

```
pip install --upgrade pip
pip install --upgrade google-api-python-client requests bs4 lxml httplib2 apiclient py-dateutil
```


### Debian & Ubuntu

```
apt install python3-googleapi python3-bs4 python3-lxml python3-requests python3-httplib2 python3-dateutil
```


## Google API key

- Go to https://console.developers.google.com/apis/credentials
- Create an "OAuth 2.0 client ID"
- Download the JSON file from the OAuth 2 client ID page and save it as client_secret.json
- Run the script once to authenticate

More information here: https://developers.google.com/gmail/api/quickstart/python

