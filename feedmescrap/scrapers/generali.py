from datetime import datetime
import json
import urllib2

from feedmescrap import Article

def scrape():

    url = 'https://generali.taleo.net/careersection/rest/jobboard/searchjobs?lang=en&portal=101430233'
    request_payload= '{"filterSelectionParam":{"activeFilterId":"LOCATION","searchFilterSelections":[{"id":"LOCATION","selectedValues":["305100493"]}]},"multilineEnabled":false,"pageNo":1,"sortingSelection":{"ascendingSortingOrder":"false","sortBySelectionParam":"5"}}'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/json'
    }
    
    request = urllib2.Request(url, data=request_payload, headers=headers) 
    r = urllib2.urlopen(request).read()
    response = json.loads(r)

    items = []

    for job in response['requisitionList']:
        try:
            fields = job['column']
            title = fields[0]
            url = "https://generali.taleo.net/careersection/ex/jobdetail.ajax?requisitionno={}".format(job['contestNo'])
            author = fields[2]

            items.append(Article(
                title= title,
                url= url,
                summary='',
                updated=datetime.now(),
                author=fields[2]
            ))
        except:
            print('cannot parse json piece: {}'.format(job))
            raise

    return items


if __name__ == '__main__':

    for i in scrape(): print(i)
    
