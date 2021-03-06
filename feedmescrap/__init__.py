import importlib
import pkgutil
import sys

def get_all_scrapers():
    scrapers = [name for _, name, _ in pkgutil.iter_modules(['scrapers'])]
    if len(scrapers)==0:
        scrapers = [name for _, name, _ in pkgutil.iter_modules(['feedmescrap/scrapers'])]
    return scrapers

def scrape(scraper_name):
   
    try:
        scraper = importlib.import_module("feedmescrap.scrapers."+scraper_name)
        add_scraper_name = lambda article: [article, setattr(article, "scraper" ,scraper_name)][0]
        return [add_scraper_name(a) for a in scraper.scrape()] 
    except ImportError:
        print "Scraper name does not match any module: "+scraper_name
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    return False
    


class Article():

    def __init__(self, title, url, summary, updated, author, scraper=""):
        self.title=title
        self.url=url
        self.summary=summary
        self.updated=updated
        self.author=author
        self.scraper=scraper

    def __str__(self):
        return str(self.__dict__)
