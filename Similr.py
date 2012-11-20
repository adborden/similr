from math import sqrt
import re

import models
from HTMLSource import HTMLSource

DEBUG = True
context = { 'database': 'similr.db3' }

class Plugin(object):
    all_msg_handlers = ['message_handler']

    def message_handler(self, msg, args):
        re.match(r'([\{\(\[<"\'])?https?://[^\s]+\1?', msg)
        

class Similr(object):

    def __init__(self):
        self.__stats = {}

    def add(self, message):
        #if not source_parser:
        #    #TODO factory or something based on source
        #    source_parser = HTMLSource(self.source)

        source_parser = HTMLSource(message.url)
        source_parser.fetch()

        article = models.Article()
        article.source = source_parser.source
        article.author = source_parser.author
        article.published = source_parser.published
        article.publisher = source_parser.publisher
        if message.timestamp:
            article.posted = message.timestamp
        if message.author:
            article.posted_by = message.author

        tokens = article.tokens
        count = 0
        tokenizer = source_parser.tokenizer()
        for t in iter(tokenizer):
            token = t.lower()
            if token not in tokens:
                tokens[token] = 0

            tokens[token] += 1
            count += 1

        #while True:
        #    try:
        #        token = tokenizer.next().lower()
        #    except StopIteration:
        #        break

        #    if token not in tokens:
        #        tokens[token] = 0

        #    tokens[token] += 1
        #    count += 1

        article.save(context)

        if DEBUG:
            self.__stats.update({
                'tokenizer': tokenizer.stats(),
                'count': count,
            })

        return article

    def compare(self, s1, s2):
        a = s1.tokens
        b = s2.tokens
        d = reduce(lambda x, y: x+y, map(lambda i: a[i]*b[i] if i in b else 0, a))
        m = sqrt(sum(map(lambda x: x*x, s1.tokens.values())) * sum(map(lambda x: x*x, s2.tokens.values())))
        self.__stats['%s:%s' % (id(s1), id(s2))] = {
            'counts': (len(a), len(b)),
            'sums': (sum(a.values()), sum(b.values())),
            'd': d,
            'm': m,
            'stats': (s1.stats(), s2.stats()),
        }
        return d/m

    def stats(self):
        return self.__stats
