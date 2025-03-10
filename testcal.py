#!/usr/bin/python3
# ------------------------------------------------------------------------------
#
# WHO
#
#  km@grogg.org
#
# WHEN
#
# WHAT
#
#  - Test functions against Google Calendar
#  - Use this to register credentials the first time you connect
#
# ------------------------------------------------------------------------------
# Imports
import argparse
import datetime
from dcal import CineCal

# ------------------------------------------------------------------------------


def main(args):

    # Connect to Google calendar
    cinecal = CineCal(args)

    # Split date and time variables and join to datetime
    eventtime = [int(x) for x in args.date.split('-')]
    eventtime = eventtime + [int(x) for x in args.time.split(':')]
    eventtime = datetime.datetime(*eventtime)
    print("DATETIME: %s\n" % eventtime)

    # Get event
    event = cinecal.get(eventtime, "")
    print(event)

    return

# ------------------------------------------------------------------------------


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='testcal')
    parser.add_argument('--date', '-d', type=str, required=True,
                        help='Date in YYYY-MM-DD format')
    parser.add_argument('--time', '-t', type=str, required=True,
                        help='Time in HH:MM format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose')
    args = parser.parse_args()
    main(args)
