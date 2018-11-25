#------------------------------------------------------------------------------
#
# WHO
#
#  km@grogg.org
#
# WHEN
#
#  2016-02-09 Initial script
#  2016-02-10 Added Google calendar function
#  2016-02-15 Remade script into a class/module
#
# WHAT
#
#  - Scrape cinemateket for movies
#  - Parse each movie page for detailed information
#
# TODO
#
#  - ...
#
#------------------------------------------------------------------------------
# imports {{{
import re
import requests
import datetime
import httplib2
import oauth2client
from bs4 import BeautifulSoup as bs
from apiclient import discovery
from oauth2client import client
from oauth2client import tools

# }}}

# class Cinemateket() {{{
#------------------------------------------------------------------------------
class Cinemateket():

# }}}
# def __init__(self) {{{
#------------------------------------------------------------------------------
	def __init__(self, num_movies = 0):

		# Cinemateket
		self.site = 'http://www.filminstitutet.se'
		self.index = '/sv/se-och-samtala-om-film/cinemateket-stockholm/program/?eventtype=&listtype=&page=20'
		self.movies = []

		self.__import_movies(num_movies)

		return None


# }}}
# def __get_html_page(self, url) {{{
#------------------------------------------------------------------------------
	def __get_html_page(self, url):
		"""Get page from URL and return as a soup object.

		returns bs
		"""

		# HTTP GET content
		html = requests.get(self.site + url)

		# soupify and return a soup object
		# lxml is a more forgiving parser and skips som errors
		return bs(html.text, 'lxml')


# }}}
# def __get_movie_details(self, name, link, date, theater) {{{
#------------------------------------------------------------------------------
	def __get_movie_details(self, name, link, date, theater):
		"""Get and parse movie details.

		Returns dictionary
		"""

		# This div contains the movie information divided in paragraphs
		div = self.__get_html_page(link).find('div', 'article__editorial-content')

		# Movie facts is in the third paragraph
		p_facts = str(div.find_all('p')[2])

		# Create a dictionary and prepopulate som values that are not
		# always there
		movie = {}
		movie['år'] = '-'
		movie['format'] = '-'

		for line in p_facts.split("\r\n"):

			try:
				line.rstrip('<br>').strip().replace(u'\xa0', ' ')
				key   = line.split(':')[0].lower()
				value = line.split(':')[1].rstrip('<br>').strip()
				movie[key] = value.replace(u'\u2013', '-')

			except (IndexError, ValueError):
				continue

		# Create dictionary
		movie['namn'] = name.replace(u'\u2013', '-')
		movie['länk'] = self.site + link
		movie['start'] = date
		movie['teater'] = theater
		# Fix for Windows where a final <br/ is included with the year (!?)
		movie['år'] = (movie['år'].split('<'))[0]

		# Compute datetime for movie end
		times = {}
		
		# Extract hour and minutes from 'längd'
		for time in re.findall('(\d+) (\w+)', movie['längd']):
			times[str(time[1])] = int(time[0])
		try:
			times['tim'] = times['hr']
		except KeyError:
			pass
		# Change movie['längd'] to a dictionary so we can add to it below
		movie['längd'] = {}

		# http://stackoverflow.com/questions/20145902/how-to-extract-dictionary-single-key-value-pair-in-variables
		for unit in ('tim', 'min'):
			try:
				movie['längd'][unit] = times[unit]
			except KeyError:
				movie['längd'][unit] = 0
			except TypeError:
				print(unit + ": " + movie['längd'])

		# Calculate end time
		movie['slut'] = movie['start'] + datetime.timedelta(hours=movie['längd']['tim'],
			minutes=movie['längd']['min'])

		return movie

# }}}
# def __import_movies(self, max_movies) {{{
#
#
#------------------------------------------------------------------------------
	def __import_movies(self, max_movies):
		"""Get movies and store in a dictionary. Create a list of dictionaries
		and store in object.

		Returns None.
		"""

		num_movies = 0

		# Loop articles and extract key values
		for article in self.__get_html_page(self.index).find_all('article', 'promoted-item'):
			try:
				name = article.h3.string
			except AttributeError:
				continue

			link = article.a['href']
			year = (datetime.datetime.now()).year
			date = datetime.datetime.strptime(article.span.string[4:] +
				' ' + str(year), '%d/%m kl. %H:%M %Y')
			theater = article.find_all('span')[1].string

			# Get the details from the specific movie page
			movie = self.__get_movie_details(name, link, date, theater)

			num_movies = num_movies + 1
			self.movies.append(movie)
			if max_movies != 0 and num_movies >= max_movies:
				break

		return None


# }}}
# def count(self) {{{
#
#------------------------------------------------------------------------------
	def count(self):
		return len(self.movies)

# }}}
# def list(self) {{{
#
#------------------------------------------------------------------------------
	def list(self):
		return self.movies

# }}}
# def pop(self) {{{
#
#------------------------------------------------------------------------------
	def pop(self):
		return self.movies.pop()

# }}}
# def print(self) {{{
#
#------------------------------------------------------------------------------
	def print(self):

		for movie in self.movies:
			print(
				movie['start'].strftime('%Y-%m-%d %H:%M') +
				"-" +
				movie['slut'].strftime('%H:%M') +
				"\t" +
				movie['namn'] + 
				"\t" +
				movie['år'].replace(u'\u2013', '-')
			)
		return

# }}}
