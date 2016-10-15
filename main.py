from datetime import datetime
from flask import Flask, request
from operator import attrgetter
import feedmescrap.persistence.ptinydb as persistence
import feedmescrap
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed

app = Flask(__name__)



def make_external(url):
    return urljoin(request.url_root, url)


@app.route("/refresh/<scraper_name>")
def refresh(scraper_name):
    items = feedmescrap.scrape(scraper_name)
    if not items:
        return "invalid scraper name"
    inserted = 0
    for item in items:
        if not persistence.exists(item.url):
            persistence.insert(item)
            inserted += 1
    return "{} article scraped, {} inserted".format(len(items), inserted)


@app.route("/drop")
def drop():
    persistence.drop()
    return "db data dropped"


@app.route("/feed/<scraper_name>.atom")
def feed(scraper_name):
    feed = AtomFeed('Recents',feed_url=request.url, url=request.url_root)
    items = sorted( persistence.findRecent(scraper_name), key= lambda k : k.updated, reverse=True)

    if not items is None:
        for item in items:
            feed.add(
                item.title, 
                item.summary,
                content_type='html',
                author=item.author,
                url=make_external(item.url),
                updated= item.updated
            )
    return feed.get_response()


if __name__ == "__main__":
    app.run()

