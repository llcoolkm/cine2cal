# Cine2cal

Scrape Cinemateket web site for movies and create events in Google calendar.

Everything is written in Python 3 by David Hendén (km@grogg.org).


## Files

* cine2cal.py - Main script
* cinemateket.py - Module for handling Cinematekets web site
* dcal.py - Module for handling Google Calendar
* testcal.py - Script to extract calendar events

You also need a google API key file: client_secret.json


## Modules

You need to install some modules:

### Windows

pip install --upgrade pip
pip install --upgrade google-api-python-client requests bs4 lxml httplib2 oauth2client apiclient dateutil


### Debian & Ubuntu

apt install python3-googleapi python3-oauth2client python3-bs4 python3-lxml python3-requests python3-oauth2client python3-httplib2 python3-dateutil


### CentOS 6

yum -y install python34 python34-devel python34-setuptools
cd /usr/lib/python3.4/site-packages/
python3 easy_install.py pip
pip3 install --upgrade pip
pip3 install --upgrade google-api-python-client requests bs4 python-lxml httplib2 oauth2client apiclient dateutil


## Google API key

- Go to https://console.developers.google.com/apis/credentials
- Create an "OAuth 2.0 client ID"
- Download the JSON file from the OAuth 2 client ID page and save it as client_secret.json
- Run the script once to authenticate

More information here: https://developers.google.com/gmail/api/quickstart/python


