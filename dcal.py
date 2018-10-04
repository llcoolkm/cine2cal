#!/usr/bin/python
#------------------------------------------------------------------------------
#
# WHO
#
#  km@grogg.org
#
# WHEN
#
#  2016-02-15 Initial script
#
# WHAT
#
#  - Provide methods for manipulating events in a Google calendar
#
#------------------------------------------------------------------------------
# imports {{{
from __future__ import print_function
import os
import datetime
import oauth2client
from httplib2 import Http
from apiclient import discovery
from oauth2client import file, client, tools

# }}}
# class CineCal() {{{
#------------------------------------------------------------------------------
class CineCal():

	def __init__(self):

		self.name = 'dcal'
		self.scopes = 'https://www.googleapis.com/auth/calendar'
		self.apikeyfile = 'client_secret.json'
		self.timezone = 'Europe/Stockholm'
		self.attendees = ['km@grogg.org']
		self.tag = 'CINEMATEKET'

		self.__connect_calendar()

		return None


# }}}
# def __get_credentials(self) {{{
#------------------------------------------------------------------------------
	def __get_credentials(self):
		"""Gets valid user credentials from storage.

		If nothing has been stored, or if the stored credentials are invalid,
		the OAuth2 flow is completed to obtain the new credentials.

		Returns:
		Credentials, the obtained credential.
		"""
		home_dir = os.path.expanduser('~')
		credential_dir = os.path.join(home_dir, '.credentials')
		if not os.path.exists(credential_dir):
			os.makedirs(credential_dir)
		credential_path = os.path.join(credential_dir, self.apikeyfile)

		store = oauth2client.file.Storage(credential_path)
		credentials = store.get()

		if not credentials or credentials.invalid:
			flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
			flow = client.flow_from_clientsecrets(self.apikeyfile, self.scopes)
			flow.user_agent = self.name
			credentials = tools.run_flow(flow, store, flags)
			print('Storing credentials to %s' % credential_path)

		return credentials


# }}}
# def __connect_calendar(self) {{{
#------------------------------------------------------------------------------
	def __connect_calendar(self):

		credentials = self.__get_credentials()
		http = credentials.authorize(Http())
		self.service = discovery.build('calendar', 'v3', http=http)

		return None


# }}}
# def get_event() {{{
#------------------------------------------------------------------------------
	def get(self, time_event, movie_name):
		"""Get a single event from the calendar
		Look for an event that starts at the same date, has the
		correct tag and the same name.

		"""

		myevent = None

		# Set time to match the entire day
		time_min = time_event.replace(hour = 0, minute = 0, second = 0)
		time_max = time_event.replace(hour = 23, minute = 59, second = 59)

		# Retrieve all events
		eventsResult = self.service.events().list(
				calendarId = 'primary',
				timeMin = time_min.isoformat() + 'Z',
				timeMax = time_max.isoformat() + 'Z'
			).execute()


		# Loop over retrieved events
		for event in eventsResult.get('items', []):

			# Cast calendar time to datetime object
			event['start']['dateTime'] = datetime.datetime.strptime(
				event['start']['dateTime'],
				"%Y-%m-%dT%H:%M:00+02:00")

			print("Found event in calendar: %s"
				% event['start']['dateTime'], event['summary'])

			# Set myevent, Break (and return) if this event has
			# correct tag and the same name
			if event['description'].split(':')[0] == self.tag:
				if event['summary'] == movie_name:
					myevent=event
					break

		return myevent


# }}}
# def list(self, days) {{{
#------------------------------------------------------------------------------
	def list(self, days):
		"""Get events for the past X days
		"""

		if days == 0:
			return
		elif days < 0:
			# Blast from the past!
			time_max = datetime.datetime.utcnow()
			time_min = time_max - datetime.timedelta(days=abs(days))
		else:
			# Return to the future!
			time_min = datetime.datetime.utcnow()
			time_max = time_min + datetime.timedelta(days=days)

		page_token = None
		event_ids = []

		while True:
			events = self.service.events().list(
					calendarId='primary',
					timeMin=time_min.isoformat() + 'Z',
					timeMax=time_max.isoformat() + 'Z',
					pageToken=page_token
				).execute()

			for event in events['items']:
				if event['description'].split(':')[0] == self.tag:
					event_ids.append(event['id'])

			page_token = events.get('nextPageToken')
			if not page_token:
				break

		return event_ids


# }}}
# def delete(self, event_id) {{{
#------------------------------------------------------------------------------
	def delete(self, event_id):
		"""Delete a single event

		Returns None
		"""

		self.service.events().delete(calendarId='primary',
			eventId=event_id).execute()

		return None

# }}}
# def delete_days(self, days=-1) {{{
#------------------------------------------------------------------------------
	def delete_days(self, days=-1):
		"""Delete events from the current day, use negative days for past
		events.

		Default is 1 day backwards.

		Returns number of deleted events.
		"""

		num_events = 0
		for event_id in self.list(days):
			self.delete(event_id)
			num_events = num_events + 1

		return num_events


# }}}
# def insert_event(self, movie) {{{
#------------------------------------------------------------------------------
	def insert(self, movie):
		"""Create a single event in the calendar. Takes a movie dictionary as
		input.

		returns None
		"""

		event = {
			'summary': movie['namn'],
			'location': movie['teater'],
			'description': "%s:\n%s\n%s\n%s\n" %
			    (self.tag, movie['år'], movie['format'], movie['länk']),
			'start': {
				'dateTime': movie['start'].strftime('%Y-%m-%dT%H:%M:00'),
				'timeZone': self.timezone
			},
			'end': {
				'dateTime': movie['slut'].strftime('%Y-%m-%dT%H:%M:00'),
				'timeZone': self.timezone
			},
			'attendees': [
				{'email': self.attendees }
			],
			'reminders': {
				'useDefault': False,
				'overrides': [
		      			{'method': 'email', 'minutes': 24 * 60},
		      			{'method': 'popup', 'minutes': 60},
				],
			},
		}

		event = self.service.events().insert(
			calendarId='primary', sendNotifications=False, body=event
			).execute()
		print('Event created: %s' % (event.get('htmlLink')))

		return None

# }}}
