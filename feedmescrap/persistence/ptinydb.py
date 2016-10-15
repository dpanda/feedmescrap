from datetime import datetime, timedelta
#from .. import Article
from tinydb import TinyDB, Query, Storage
from tinydb_serialization import Serializer, SerializationMiddleware

# implementation of feedscraper persistence layer with tinydb

class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime  # The class this serializer handles

    def encode(self, obj):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')

    def decode(self, s):
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')

serialization = SerializationMiddleware()
serialization.register_serializer(DateTimeSerializer(), 'TinyDate')

db = TinyDB("./feedentries.json", storage=serialization)

def exists(url):
    entry = Query()
    return db.count(entry.url == url ) >= 1

def insert(article):
    db.insert(article.__dict__)

def drop():
    db.purge()

def findRecent(scraperName, maxAgeInDays=7):
    entry = Query()

    delta = timedelta(days=maxAgeInDays)
    now = datetime.now()

    test_if_recent = lambda u: ( u > now - delta)
    items_dict = db.search(
        (entry.updated.test(test_if_recent))
        &
        (entry.scraper == scraperName)
    )
    convert_to_class = lambda d : type("Article",(object,),d) 
    return [convert_to_class(d) for d in items_dict]

    
