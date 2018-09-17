#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------
# Imports {{{
import argparse
from cinemateket import Cinemateket
from dcal import CineCal

# }}}
# Parse arguments {{{
parser = argparse.ArgumentParser(description='cine2cal')
parser.add_argument('--delete', '-d', type=int, default=7,
	help='How many days into the past to delete old events')
parser.add_argument('--limit', '-l', type=int, default=0,
	help='Limit how many movies to process')
parser.add_argument('--notification', '-n', action='store_true',
	help='Enable notifications for calendar events')
parser.add_argument('--verbose', '-v', action='store_true', help='Verbose')
args = parser.parse_args()


# }}}
# def main(args) {{{
#------------------------------------------------------------------------------
def main(args):

	# Get movies from cinemateket
	cinemateket = Cinemateket(args.limit)

	print('Imported %s movies' % (str(cinemateket.count())))
	print(79 * '-')
	cinemateket.print()

	# Connect to Google calendar
	cinecal = CineCal()

	# Delete the past
	print('Deleted %i events' % (cinecal.delete_days(0 - args.delete)))

	# Insert new events
	num_events = 0
	for movie in cinemateket.list():
		event = cinecal.get(movie['start'])
		if event is None:
			cinecal.insert(movie)
			num_events = num_events + 1

	print('Inserted %i events' % (num_events))


if __name__ == '__main__':
	main(args)


# }}}

