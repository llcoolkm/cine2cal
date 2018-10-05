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

pip install --upgrade google-api-python-client requests bs4 httplib2 oauth2client apiclient

### Debian

pip install --upgrade google-api-python-client requests bs4 httplib2 oauth2client apiclient

### CentOS 6

yum -y install python34 python34-devel python34-setuptools
cd /usr/lib/python3.4/site-packages/
python3 easy_install.py pip
pip3 install --upgrade pip
pip3 install --upgrade google-api-python-client requests bs4 httplib2 oauth2client apiclient


## Google API key

https://developers.google.com/gmail/api/quickstart/python

