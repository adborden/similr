from datetime import datetime

from models import Article
from HTMLSource import HTMLSource
from Similr import Similr

url = 'http://www.cnn.com/2012/09/25/tech/social-media/facebook-private-messages/index.html'
url2 = 'http://bits.blogs.nytimes.com/2012/09/25/japanese-look-for-alternatives-to-apples-maps/'
url3 = 'http://bits.blogs.nytimes.com/2012/09/25/rivals-pile-on-apple-maps/'
context = {
    'database': 'similr.db3'
}

#source2 = HTMLSource(url2)
#source3 = HTMLSource(url3)
#article1 = Article()
#article1.fetch(source2)
#article1.save(context)
#article2 = Article()
#article2.fetch(source3)
#article2.save(context)
similr = Similr()

#article3 = Article()
#article3.source = url2
#article4 = Article()
#article3.id = 1
#article4.id = 2
#article3.load(context)
#article4.load(context)
#print 'stats:', repr(similr.stats())
#print 'similarity:', similr.compare(article3, article4)
class Message:
  pass

message = Message()
message.timestamp = datetime.now()
message.author = 'Aaron'
message.url = url2
article = similr.add(message)

message3 = Message()
message3.timestamp = datetime.now()
message3.author = 'Aaron'
message3.url = url3
article3 = similr.add(message3)

print 'similarity:', similr.compare(article, article3)

exit(0)

tokenizer = source.tokenizer()
if not tokenizer:
    print "Oh noes!"
tokens = {}
count = 0
while True:
    try:
        token = tokenizer.next().lower()
    except StopIteration:
        break

    print 'token:', token
    if token not in tokens:
        tokens[token] = 0

    tokens[token] += 1
    count += 1

print 'tokenizer stats:', repr(tokenizer.get_stats())
print 'tokens:', repr(tokens)
print 'total tokens:', count
