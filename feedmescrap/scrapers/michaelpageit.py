from bs4 import BeautifulSoup
from datetime import datetime
from feedmescrap import Article
import urllib

def scrape_page(page):
    print("Scraping MichaelPage, "+str(page))
    items = []

    r = urllib.urlopen('http://www.michaelpage.it/browse/jobs/information-technology/all/all?page='+str(page)).read()
    soup = BeautifulSoup(r,"html.parser")

    entries = soup.select("div.jobresults > .view-content > .item-list > ul > li")

    for entry in entries:

        title="(no title)"
        summary=""
        url='http://www.michaelpage.it'

        try:
            h2_a = entry.select("h2 a")[0]
            title = h2_a.string
            url += h2_a.get("href")
        except IndexError:
            print("Check css selector for title, not appearing anymore in html")
        
        for selector in ["div.job-summary",".item-list ul"]:
            try:
                jobsummary = entry.select(selector)[0]
                summary+= str(jobsummary)
            except IndexError:
                print("Check css selector for summary, not appearing anymore in html")
                summary+="(no summary)"
        
        items.append(Article(
            title=title,
            url=url,
            summary=summary,
            updated=datetime.now(),
            author="MichaelPage"
        ))

    return items


def scrape():
    items =[]
    page = 0
    max_page = 20
    while True:
        page_items = scrape_page(page)
        if len(page_items)==0:
            break
        items.extend(page_items)
        page += 1
        if page>=max_page:
            break
    return items