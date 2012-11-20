import urllib2

from HTMLParser import HTMLParser
DEBUG = True

class HTMLSource(object):
    """Handles HTML sources"""

    def __init__(self, url):
        self.author = None
        self.published = None
        self.publisher = None
        self.source = url
        self.reponse = None
        pass

    def fetch(self):
        response = urllib2.urlopen(self.source)
        if not response:
            return

        # Check for redirects
        if self.source != response.geturl():
            self.source = response.geturl()

        self.response = response

    def tokenizer(self):
        if not self.response:
            return None

        tokenizer = HTMLTokenizer()
        tokenizer.tokenize(self.response)
        return tokenizer

class HTMLTokenizer(HTMLParser):
    _tokens = []
    _tags = []
    _ignore_tags = ['script', 'style']
    _iter = None
    __stats = {'tags': set(), 'tokens': set()}
    charset = 'utf-8'

    def tokenize(self, content):
        self._content = content

    def next(self):
        while not len(self._tokens):
            try:
                self.fill()
            except StopIteration:
                break

        if not len(self._tokens):
            raise StopIteration

        return self._tokens.pop(0)

    def fill(self):
        if not self._iter:
            self._iter = iter(self._content)

        while not len(self._tokens):
            line = self._iter.next()
            self.feed(line)

    def handle_starttag(self, tag, attrs):
        if tag == 'meta' and 'charset' in attrs:
            self.charset = attrs['charset']

        if tag in self._ignore_tags:
            self._tags.append(tag)

        if DEBUG:
            self.__stats['tags'].add(tag)

    def handle_endtag(self, tag):
        if tag in self._ignore_tags \
           and len(self._tags) \
           and tag == self._tags[-1]:
            self._tags.pop()

    def handle_data(self, data):
        if len(self._tags):
            return

        #TODO remove punctuation
        try:
            tokens = [t.decode(self.charset) for t in data.split(' ') if t not in ['\n','\r\n', '', '|']]
            self._tokens.extend(tokens)
            if DEBUG:
                self.__stats['tokens'].update(tokens)

        except UnicodeDecodeError, e:
            print 'Failed to parse line:', { 'exception': e, 'line': self.getpos(), 'url': self.url}

    def stats(self):
        return self.__stats

    def __iter__(self):
        return self

