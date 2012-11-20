from datetime import datetime
import sqlite3

DEBUG = True

class DataModel(object):
    def __init__(self):
        self.id = 0
        self.created = None
        self._stats = {}

    def exists(self):
        return self.id != 0

    def load_from(self, row):
        for k in row.keys():
            self.__setattr__(k, row[k])

    def load(self, context):
        conn = sqlite3.connect(context['database'], detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM %s WHERE id = ?' % self._collection_name(), (self.id,))
        r = c.fetchone()
        self.load_from(r)
        conn.close()

    #def save(self, context):
    #    fields = self._fields()
    #    conn = sqlite3.connect(context['database'])
    #    c = conn.cursor()
    #    c.execute('INSERT INTO %s (%s) VALUES (%s)' % (self._collection_name(), ','.join(fields.keys()), ','.join(fields.values())))

    def stats(self):
        return self._stats

    def _collection_name(self):
        return type(self).__name__

    #def _fields(self):
    #    fields = [f for f in self.__dict__ if not f.startswith('_')]

class Article(DataModel):

    def __init__(self):
        super(Article, self).__init__()
        self.source = None
        self.author = None
        self.publisher = None
        self.published = None
        self.posted_by = None
        self.posted = None
        self.tokens = {}

    def fetch(self, source_parser = None):
        """Deprecated or something"""
        if not source_parser:
            #TODO factory or something based on source
            source_parser = HTMLSource(self.source)

        source_parser.fetch()

        self.tokens = tokens = {}
        self.count = count = 0
        self.source = source_parser.url
        tokenizer = source_parser.tokenizer()

        #TODO Fix this
        while True:
            try:
                token = tokenizer.next().lower()
            except StopIteration:
                break

            if token not in tokens:
                tokens[token] = 0

            tokens[token] += 1
            count += 1

        if DEBUG:
            self._stats['tokenizer'] = tokenizer.stats()

    def load(self, context):
        conn = sqlite3.connect(context['database'], detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM Article WHERE id = ?', (self.id,))
        r = c.fetchone()
        self.load_from(r)

        # Load Vector
        c.execute('SELECT * FROM Vector WHERE article_id = ?', (self.id,))
        rows = c.fetchmany(256)
        while len(rows):
            for r in rows:
                self.tokens[r['word']] = r['count']
            rows = c.fetchmany(256)

        conn.close()

    def save(self, context):
        if self.exists():
            raise Error("Data already exists in store")

        self.created = datetime.now()
        conn = sqlite3.connect(context['database'], detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        c = conn.cursor()
        c.execute('INSERT INTO Article (created, source, author, publisher, published, posted_by, posted) VALUES (?, ?, ?, ?, ?, ?, ?)', (self.created, self.source, self.author, self.publisher, self.published, self.posted_by, self.posted))
        c.execute('SELECT LAST_INSERT_ROWID()')
        self.id, = c.fetchone()

        # Save the Vector
        rows = [(self.created, self.id, word, self.tokens[word]) for word in self.tokens]
        c.executemany('INSERT INTO Vector (created, article_id, word, count) VALUES (?,?,?,?)', rows)

        conn.commit()
        conn.close()
