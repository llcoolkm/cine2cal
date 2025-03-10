# ------------------------------------------------------------------------------
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
# ------------------------------------------------------------------------------
# imports
from __future__ import print_function
from __future__ import annotations
import os
import sys
import json
import logging
from datetime import datetime, timedelta  # Fix: import timedelta separately
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dateutil.parser import parse
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from cinemateket import Movie

# ------------------------------------------------------------------------------


@dataclass
class CalendarEvent:
    """Represents a calendar event with all necessary details"""
    summary: str
    location: str
    description: str
    start_time: datetime
    end_time: datetime
    timezone: str
    attendees: List[str]


class CineCal():
    """Class for managing Google Calendar events"""

    def __init__(self,
                 args: Any,
                 timezone: str = 'Europe/Stockholm',
                 attendees: Optional[List[str]] = None,
                 tag: str = 'CINEMATEKET') -> None:

        self.verbose: bool = args.verbose
        self.credentials_file: str = 'client_secret.json'
        self.attendees: List[str] = attendees or ['km@grogg.org']
        self.name: str = 'dcal'
        self.scopes: str = 'https://www.googleapis.com/auth/calendar'
        self.tag: str = tag
        self.timezone: str = timezone
        self.service: Any = None
        self._connect_calendar()

# ------------------------------------------------------------------------------

    def _get_credentials(self) -> Credentials:
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials object
        """
        creds = None
        token_dir = os.path.join(os.path.expanduser('~'), '.credentials')
        if not os.path.exists(token_dir):
            os.makedirs(token_dir)
        token_file = os.path.join(token_dir, 'calendar-token.json')

        if os.path.exists(token_file):
            try:
                # workaround for
                # https://github.com/googleapis/google-auth-library-python/issues/501
                with open(token_file, 'r') as stream:
                    creds_json = json.load(stream)
                creds = Credentials.from_authorized_user_info(creds_json)
                creds.token = creds_json['token']
                if self.verbose:
                    print(f'Loaded credentials from {token_file}')

            except Exception as e:
                sys.stderr.write(f'Failed to load existing credentials: {e}\n')
                os.remove(token_file)
                return self._get_credentials()

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.token:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Missing {self.credentials_file}. Download it from G"
                        "oogle Cloud Console and place it in the project root."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, [self.scopes])
                creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                creds_data = {
                    'token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_uri': creds.token_uri,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'scopes': creds.scopes
                }

                with open(token_file, 'w') as token:
                    json.dump(creds_data, token)
                    if self.verbose:
                        print(f'Saved creds to {token_file}')

        return creds

# ------------------------------------------------------------------------------

    def _connect_calendar(self) -> None:
        """Connect to Google calendar"""

        if not os.path.exists(self.credentials_file):
            raise Exception(
                f'Missing {self.credentials_file} file. Please download it'
                f'from Google Cloud Console and place it in the project root'
                f'directory.')

        try:
            credentials = self._get_credentials()
            self.service = build(
                'calendar', 'v3',
                credentials=credentials,
                cache_discovery=False)
        except Exception as e:
            logging.error(f'Failed to connect to calendar: {e}')

# ------------------------------------------------------------------------------

    def get(self, time_event: datetime, movie_name: str) -> Optional[Dict[str, Any]]:
        """Get a single event from the calendar
        Look for an event that starts at the same date, has the
        correct tag and the same name."""

        try:
            time_min = time_event.replace(hour=0, minute=0, second=0)
            time_max = time_event.replace(hour=23, minute=59, second=59)

            events = self.service.events().list(
                calendarId='primary',
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime').execute()
        except Exception as e:
            sys.stderr.write(f'Failed to fetch events: {e}\n')
            return None

        # Loop over retrieved events
        for event in events.get('items', []):

            # Convert calendar time to datetime object with dateutil
            event['start']['dateTime'] = parse(event['start']['dateTime'])

            # Set myevent, Break (and return) if this event has
            # correct tag and the same name
            if (event['description'].split(':')[0] == self.tag and
                    movie_name in event['summary']):
                if self.verbose:
                    print(f"Found event in calendar: "
                          f"{event['start']['dateTime']} "
                          f"{event['summary']}")
                return event

        return None

# ------------------------------------------------------------------------------

    def list(self, days: int) -> List[str]:
        """Get events for the past X days"""

        # Blast from the past!
        if days < 0:
            time_max = datetime.utcnow()
            time_min = time_max - timedelta(days=abs(days))
        # Return to the future!
        elif days > 0:
            time_min = datetime.utcnow()
            time_max = time_min + timedelta(days=days)
        else:
            return []

        page_token = None
        event_ids: List[str] = []

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

# ------------------------------------------------------------------------------

    def delete(self, event_id: str) -> None:
        """Delete a single event"""

        self.service.events().delete(calendarId='primary',
                                     eventId=event_id).execute()

# ------------------------------------------------------------------------------

    def delete_days(self, days: int = -1) -> int:
        """Delete events from the current day, use negative days for past
        events.

        Default:
            days is 1 day back in time.

        Returns:
            number of deleted events.
        """

        num_events = 0
        for event_id in self.list(days):
            self.delete(event_id)
            num_events += 1

        return num_events

# ------------------------------------------------------------------------------

    def insert(self, movie: Movie) -> None:
        """Create a single event in the calendar.

        Args:
            movie: MovieEvent object containing event details

        Raises:
            Exception: If event creation fails
        """

        event = self._build_event(movie)
        try:
            created_event = self.service.events().insert(
                calendarId='primary',
                sendNotifications=False,
                body=event).execute()
            print(f'Event created: {created_event.get("htmlLink")}')
        except Exception as e:
            sys.stderr.write(f'Failed to create event: {e}')

# ------------------------------------------------------------------------------

    def _build_event(self, movie: Movie) -> Dict[str, Any]:
        """Builds event dictionary from movie data."""

        return {
            'summary': movie.name,
            'location': movie.theater,
            'description': f"{self.tag}:\n{movie.year}\n{movie.link}",
            'start': {
                'dateTime': movie.start.isoformat(),
                'timeZone': self.timezone
            },
            'end': {
                'dateTime': movie.end.isoformat(),
                'timeZone': self.timezone
            },
            'attendees': [{'email': email} for email in self.attendees],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 60},
                ],
            },
        }
