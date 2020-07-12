import re
import textwrap
from nntplib import NNTP, decode_header
from urllib.request import urlopen


class NewsItem:
    def __init__(self, title, body):
        """
        A simple news item consisting of a title and body text.
        """
        self.title = title
        self.body = body


class NewsAgent:
    """
    An object that can distribute news items from news sources to news
    destinations.
    """

    def __init__(self):
        self.sources = []
        self.destinations = []

    def add_source(self, source):
        self.sources.append(source)

    def add_destination(self, destination):
        self.destinations.append(destination)

    def distribute(self):
        """
        Retrieve all news items from all sources, and Distribute them to all
        destinations.
        """
        items = []
        for source in self.sources:
            items.extend(source.get_items())
        for dest in self.destinations:
            dest.receive_items(items)


class PlainDestination:
    """
    A news destination that formats all its news items as plain text.
    """

    @staticmethod
    def receive_items(items):
        for item in items:
            print(item.title)
            print('-' * len(item.title))
            print(item.body)


class NNTPSource:
    """
    A news source that retrieves news items from an NNTP group.
    """

    def __init__(self, servername, group, how_many):
        self.servername = servername
        self.group = group
        self.how_many = how_many

    def get_items(self):
        server = NNTP(self.servername)
        _, count, first, last, name = server.group(self.group)
        start = last - self.how_many + 1

        _, overviews = server.over((start, last))

        for ID, over in overviews:
            title = decode_header(over['subject'])
            _, info = server.body(ID)
            body = '\n'.join(line.decode('latin') for line in info.lines)
            yield NewsItem(title, body)
        server.quit()


class SimpleWebSource:
    """
    A news source that extracts news items from a web page using regular
    expressions.
    """

    def __init__(self, url, title_pattern, body_pattern, encoding="utf-8"):
        self.url = url
        self.title_pattern = re.compile(title_pattern)
        self.body_pattern = re.compile(body_pattern)
        self.encoding = encoding

    def get_items(self):
        text = urlopen(self.url).read().decode(self.encoding)
        titles = self.title_pattern.findall(text)
        bodies = self.body_pattern.findall(text)
        for title, body in zip(titles, bodies):
            yield NewsItem(title, textwrap.fill(body) + '\n')


class HTMLDestination:
    """
    A news destination that formats all its news items as HTML.
    """

    def __init__(self, filename):
        self.filename = filename

    def receive_items(self, items):
        out = open(self.filename, 'w')
        print('''<!DOCTYPE html>
        <html lang="en">
            <head>
                <title>Today's News</title>
                <meta charset="UTF-8">
                <link rel="stylesheet" href="format.css" type="text/css"/>
            </head>
            <body>
                <h1>Today's News</h1>
        ''', file=out)
        print('<ul>', file=out)
        id = 0
        for item in items:
            id += 1
            print(' <li><a href="#{}">{}</a></li>'
                  .format(id, item.title), file=out)
        print('</ul>', file=out)

        id = 0
        for item in items:
            id += 1
            print('<h2 id="{}">{}</h2>'
                  .format(id, item.title), file=out)
            print('<pre>{}</pre>'.format(item.body), file=out)
        print("""
        </body>
        </html>
        """, file=out)


def runDefaultSetup():
    """
    A default setup of sources and destination. Modify to taste.
    """
    agent = NewsAgent()
    # A SimpleWebSource that retrieves news from Reuters:
    reuters_url = 'http://www.reuters.com/news/world'
    reuters_title = r'<h2><a href="[^"]*"\s*>(.*?)</a>'
    reuters_body = r'</h2><p>(.*?)</p>'
    reuters = SimpleWebSource(reuters_url, reuters_title, reuters_body)
    agent.add_source(reuters)
    # An NNTPSource that retrieves news from comp.lang.python.announce:
    clpa_server = 'nntp.aioe.org'
    clpa_group = 'comp.lang.python.announce'
    clpa_howmany = 10
    clpa = NNTPSource(clpa_server, clpa_group, clpa_howmany)
    agent.add_source(clpa)
    # Add plain-text destination and an HTML destination:
    agent.add_destination(PlainDestination())
    agent.add_destination(HTMLDestination('news.html'))
    # Distribute the news items:
    agent.distribute()


if __name__ == '__main__': runDefaultSetup()
