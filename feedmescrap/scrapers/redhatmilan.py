from bs4 import BeautifulSoup
from datetime import datetime
from feedmescrap import Article
import urllib

def scrape():
    print("Scraping Red Hat")
    items = []

    jobs_url='https://careers-redhat.icims.com/jobs/search?ss=1&searchLocation=13270--Milan&in_iframe=1'

    r = urllib.urlopen(jobs_url).read()
    soup = BeautifulSoup(r,"html.parser")

    entries = soup.select(".iCIMS_JobsTable.iCIMS_Table .iCIMS_JobListingRow")
    
    for entry in entries:

        title="(no title)"
        url=jobs_url
        summary="<p>No summary</p>"

        try:
            job_link = entry.select('td[itemprop="title"] a')[0]
            title= job_link.string.replace("\n","")
            url = str(job_link.get("href"))
        except IndexError:
            print("Check css selectors for title and href, item not found")

        try:
            department = entry.select('td.iCIMS_JobsTableField_4')[0]
            summary=str(department)
        except IndexError:
            print("Check css selectors for department, item not found")

        items.append(Article(
            title=title,
            url=url,
            summary=summary,
            updated=datetime.now(),
            author="Red Hat"
        ))
        print("added '{}' - {}".format(title, url))


    print("{} items scraped".format(len(items)))
    return items
