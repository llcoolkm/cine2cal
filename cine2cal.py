#!/usr/bin/env python3
# ------------------------------------------------------------------------------
#
# WHO
#
#  km@grogg.org
#
# WHAT
#
#  Parse Cinemateket page of upcoming movies and insert them into a Google
#  calendar. Uses cinemateket and dcal modules.
#
# TODO
#
#  - Calendar entry check only checks the first event in that time slot which
#    means that it will return false if the first event is not a CINEMATEKET
#    event.
#
#
# ------------------------------------------------------------------------------

import argparse
import sys

from halo import Halo

from cinemateket import Cinemateket
from dcal import CineCal


# ------------------------------------------------------------------------------

def main(args: argparse.Namespace) -> None:
    """Main function to sync Cinemateket movies to calendar"""

    try:
        # Get movies from cinemateket
        cinemateket = Cinemateket(args)
        print()
        cinemateket.print()
        print()

        # Connect to Google calendar
        cinecal = CineCal(args)

        # Delete the past
        deleted_count = cinecal.delete_days(0 - args.delete)
        print(f'Deleted {deleted_count} events.')

        # Insert new events
        if args.dry_run:
            return

        num_events = _sync_events(cinemateket, cinecal)
        print(f'Inserted {num_events} events.')

    except Exception as e:
        #        spinner.stop_and_persist(
        #            text=f'Scraped {str(cinemateket.count())} movies.')
        sys.stderr.write(f'Error occurred: {e}\n')
        sys.exit(-1)

# ------------------------------------------------------------------------------


def _sync_events(cinemateket: Cinemateket, cinecal: CineCal) -> int:
    """Sync movies to calendar and return number of inserted events"""
    num_events = 0
    for movie in cinemateket.list():
        try:
            # Get all events in this time slot
            event = cinecal.get(movie.start, movie.name)

            if not event:
                cinecal.insert(movie)
                num_events += 1
        except Exception as e:
            sys.stderr.write(f'Failed to sync movie {movie.name}: {e}\n')

    return num_events

# ------------------------------------------------------------------------------


if __name__ == '__main__':
    """main"""

    # Parse arguments
    parser = argparse.ArgumentParser(description='cine2cal')
    parser.add_argument('--delete', '-d', type=int, default=0,
                        help='How many days in the past to delete old events.')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Don\'t insert events into the calendar.')
    parser.add_argument('--movies', '-m', type=int, default=20,
                        help='Number of movies to scrape.')
    parser.add_argument('--notifications', '-N', action='store_true',
                        help='Enable notifications for calendar events.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose')
    args = parser.parse_args()
    main(args)
