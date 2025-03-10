# ------------------------------------------------------------------------------
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
# ------------------------------------------------------------------------------
# imports
import re
import requests
import datetime
from bs4 import BeautifulSoup as bs
from dataclasses import dataclass
from typing import Optional, List, Any
from tabulate import tabulate

# ------------------------------------------------------------------------------


@dataclass
class MovieLength:
    hours: int
    minutes: int


@dataclass
class Movie:
    name: str
    link: str
    start: datetime.datetime
    end: datetime.datetime
    theater: str
    year: str
    length: MovieLength


class Cinemateket():

    def __init__(self, args: Any) -> None:

        self.site = "http://www.filminstitutet.se"
        self.index = "/sv/se-och-samtala-om-film/cinemateket-stockholm/" \
                     "program/?eventtype=&listtype=&page=20"
        self.movies: List[Movie] = []
        self.verbose: bool = args.verbose

        self._import_movies(args.number)

# ------------------------------------------------------------------------------

    def _get_html_page(self, url: str) -> bs:
        """Get page from URL and return as a soup object.

        Return:
            bs
        """

        # HTTP GET content
        html = requests.get(self.site + url)
        if self.verbose:
            print(f'Fetched {len(html.text)} bytes from page'
                  f' {self.site} {url}')

        # soupify and return a soup object
        # lxml is a more forgiving parser and skips som errors
        return bs(html.text, 'lxml')

# ------------------------------------------------------------------------------

    def _get_movie_details(self, name: str, link: str,
                           date: datetime.datetime, theater: str) -> Optional[Movie]:
        """Get and parse movie details.

        Return:
            dictionary
        """

        name = name.replace(u'\u2013', '-')
        year = '-'
        length = MovieLength(hours=0, minutes=0)
        marker = "isningsmaterial"

        # This div contains the movie information divided in paragraphs
        div = self._get_html_page(link).find(
            'div', 'article__editorial-content')
        if not div:
            return None

        # Extract year, start and end of movie
        paragraphs = div.find_all('p')
        for p in paragraphs:
            if marker in p.get_text():
                filmfakta = p.get_text()
                if self.verbose:
                    print(filmfakta)

                # Extract year
                m = re.search(r'(\d{4})', filmfakta)
                year = str(m.group(1)) if m else '-'

                # Extract hours & minutes
                h_match = re.search(r'(\d+) tim', filmfakta)
                m_match = re.search(r'(\d+) min', filmfakta)
                length = MovieLength(
                    hours=int(h_match.group(1)) if h_match else 0,
                    minutes=int(m_match.group(1)) if m_match else 0
                )
                break

        # Calculate end time
        end = date + datetime.timedelta(
            hours=length.hours,
            minutes=length.minutes
        )

        return Movie(name=name, link=self.site + link, start=date, end=end,
                     theater=theater, year=year, length=length)

# ------------------------------------------------------------------------------

    def _import_movies(self, max_movies: int) -> int:
        """Get movies and store in a dictionary. Create a list of dictionaries
        and store in object.
        """

        num_movies = 0
        print('Fetching:', end='', flush=True)

        # Loop articles and extract key values
        articles = self._get_html_page(
            self.index).find_all('article', 'promoted-item')
        for article in articles:
            try:
                name = article.h3.string
                if not name:
                    continue

                link = article.a['href']
                year = (datetime.datetime.now()).year
                date = datetime.datetime.strptime(article.span.string[4:] +
                                                  ' ' + str(year),
                                                  '%d/%m kl. %H:%M %Y')
                theater = article.find_all('span')[1].string

                if self.verbose:
                    print(f'Found movie {name} shown {date} at {theater}')

                # Get the details from the specific movie page
                movie = self._get_movie_details(name, link, date, theater)

                # Add movie to the instance's movie list
                if movie:
                    num_movies += 1
                    self.movies.append(movie)
                    if not self.verbose:
                        print('.', end='', flush=True)
                    if max_movies != 0 and num_movies >= max_movies:
                        break

            except AttributeError:
                continue

        return num_movies

# ------------------------------------------------------------------------------

    def count(self) -> int:
        return len(self.movies)

# ------------------------------------------------------------------------------

    def list(self) -> List[Movie]:
        return self.movies

# ------------------------------------------------------------------------------

    def pop(self) -> Movie:
        return self.movies.pop()

# ------------------------------------------------------------------------------
    def print(self) -> None:
        """Print all movies in a formatted table"""
        table_data = [
            [
                f"{movie.start.strftime('%Y-%m-%d %H:%M')}",
                movie.name,
                movie.year,
                movie.theater,
                f'{movie.length.hours}h {movie.length.minutes}m'
            ]
            for movie in self.movies
        ]

        headers = ['Time', 'Movie', 'Year', 'Theater', 'Length']
        print(tabulate(table_data, headers=headers, tablefmt='simple'))
