# -----------------------------------------------------------------------------

import re
import datetime
from dataclasses import dataclass

from bs4 import BeautifulSoup as bs
from halo import Halo
import requests
from tabulate import tabulate


# -----------------------------------------------------------------------------

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

    def __init__(self, args) -> None:

        self.site = 'http://www.filminstitutet.se'
        self.index = '/sv/se-och-samtala-om-film/cinemateket-stockholm/' \
                     'program/?eventtype=&listtype=&page=20'
        self.movies: list[Movie] = []
        self.verbose: bool = args.verbose

        self._import_movies(args.movies)

# -----------------------------------------------------------------------------

    def _get_html_page(self, url: str) -> bs:
        """Request the URL page and return it as a soup object."""

        # HTTP GET content
        html = requests.get(self.site + url)
        if self.verbose:
            print(f'Fetched {len(html.text)} bytes from page '
                  f'{self.site} {url}')

        # soupify and return a soup object
        # lxml is a more forgiving parser and skips som errors
        return bs(html.text, 'lxml')

# ------------------------------------------------------------------------------

    def _get_movie_details(self,
                           name: str,
                           link: str,
                           date: datetime.datetime,
                           theater: str) -> Movie | None:
        """Get and parse movie details."""

        name = name.replace(u'\u2013', '-')
        year = '-'
        length = MovieLength(hours=0, minutes=0)
        marker = 'isningsmaterial'

        # This div contains the movie information divided in paragraphs
        div = self._get_html_page(link).find(
            'div', 'article__editorial-content')
        if not div or not hasattr(div, 'find_all'):
            return None

        # Extract year, start and end of movie
        paragraphs = div.find_all('p')  # type: ignore

        for p in paragraphs:
            if marker in p.get_text():
                filmfakta = p.get_text()
                if self.verbose:
                    print(filmfakta)

                # Extract year
                y_match = re.search(r'(\d{4})', filmfakta)
                year = str(y_match.group(1)) if y_match else '-'

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

# -----------------------------------------------------------------------------

    def _import_movies(self, max_movies: int) -> int:
        """Get movies and store in a dictionary. Create a list of dictionaries
        and store in object.
        """

        num_movies = 0
        # print('Fetching:', end='', flush=True)
        spinner = Halo(text='Fetching movies', spinner='dots')
        spinner.start()

        # Loop articles and extract key values
        articles = self._get_html_page(
            self.index).find_all('article', 'promoted-item')
        for article in articles[:max_movies]:
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

            except AttributeError:
                continue

        spinner.stop_and_persist(symbol=u'\N{check mark}',
                                 text=f'Fetched {max_movies} movies.')
        return num_movies

# -----------------------------------------------------------------------------

    def count(self) -> int:
        return len(self.movies)

# -----------------------------------------------------------------------------

    def list(self) -> list[Movie]:
        return self.movies

# -----------------------------------------------------------------------------

    def pop(self) -> Movie:
        return self.movies.pop()

# -----------------------------------------------------------------------------

    def print(self) -> None:
        """Print all movies in a formatted table"""
        table_data = [
            [
                f'{movie.start.strftime('%Y-%m-%d %H:%M')}',
                movie.name,
                movie.year,
                movie.theater,
                f'{movie.length.hours}h {movie.length.minutes}m'
            ]
            for movie in self.movies
        ]

        headers = ['Time', 'Movie', 'Year', 'Theater', 'Length']
        print(tabulate(table_data, headers=headers, tablefmt='simple'))
