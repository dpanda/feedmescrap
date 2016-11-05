from datetime import datetime
from flask import Flask, request, redirect
from operator import attrgetter
import os
import pkgutil
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed

import feedmescrap
import feedmescrap.persistence

app = Flask(__name__)

#default persistence implementation is tinydb
persistence_backend = os.environ.get('persistence') or "ptinydb"
persistence_impl = feedmescrap.persistence.get_persistence(persistence_backend)


def make_external(url):
    return urljoin(request.url_root, url)


@app.route("/<scraper_name>/refresh")
def refresh(scraper_name):
    items = feedmescrap.scrape(scraper_name)
    if not items:
        return "invalid scraper name"
    inserted = persistence_impl.insert_all(items)
    return "{} article scraped, {} inserted".format(len(items), inserted)

def refresh_all():
    for scraper in feedmescrap.get_all_scrapers():
        refresh(scraper)
    

@app.route("/all/drop")
def drop():
    persistence_impl.drop()
    return "db data dropped"

@app.route("/<scraper_name>/feed.atom")
def feed_atom(scraper_name):
    feed = AtomFeed('Recents',feed_url=request.url, url=request.url_root)
    articles =persistence_impl.findRecent(scraper_name)
    if articles:
        items = sorted( articles, key= lambda k : k.updated, reverse=True)
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

@app.route("/<scraper_name>/feed")
def feed(scraper_name):
    #simple redirect to feed.atom
    return redirect("{}/feed.atom".format(scraper_name), code=302)

if __name__ == "__main__":
    app.run()

