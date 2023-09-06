import requests
import pprint
import time
import json
from foolcalls.scrapers import scrape_transcript_urls_by_page, scrape_transcript, scrape_author_article_urls_by_page
import csv

# get one transcript for a known url
# transcript_url = 'https://www.fool.com/investing/2023/08/27/a-bull-market-is-coming-2-unstoppable-growth-stock/'
# response = requests.get(transcript_url)
# transcript = scrape_transcript(response.text)
# pprint.pprint(transcript)

# get all (~20) transcript urls from a single page
# transcript_urls = scrape_transcript_urls_by_page(page_num=1)
# print(transcript_urls)

# urls = scrape_author_article_urls_by_page(2, 20250)
# print(urls)

urls = []

with open('outputaa', 'r') as readData:
    readCsv = csv.reader(readData)
    data = list(readCsv)
    for d in data:
        urls.append(d[0])
#
## for i in range(20250, 20260):
##     urls = scrape_author_article_urls_by_page(1, i)
##     print(urls)
##     print("*"*100)
##     time.sleep(5) # sleep 5 seconds between reqeusts

num_before_write = 0
articles = []
data_csv = []
failures = 0
for url in urls:
    try:
        response = requests.get(url)
    except:
        failures += 1
        continue
    data = scrape_transcript(response.text)
    data['url'] = url
    data_csv.append(data)
    print(num_before_write)
    if num_before_write == 10:
        # write now
        with open('articles1.csv', 'a', newline='') as csvfile:
            # create a CSV writer object
            writer = csv.writer(csvfile)
            # write the column headers to the CSV file
            # iterate through each URL in the list
            for row in data_csv:
                # send a request to the URL and extract the data
                # write the data to the CSV file
                row = [row['url'], row['article_header'], row['date'], row['ticker'], row['article_body']]
                writer.writerow(row)
            num_before_write = 0
            data_csv = []
    else:
        num_before_write+=1
    time.sleep(2) # sleep 5 seconds between reqeusts


# # combine the two above to get a handful of transcripts from fool.com
#num_of_pages = 3 # will be ~60 transcripts, with ~20 transcript urls per page
#output = []
#for page in range(0, num_of_pages):
#    urls = scrape_transcript_urls_by_page(page)
#    # for url in urls:
#    #     response = requests.get(url)
#    #     data = scrape_transcript(response.text)
#    #     output.append(url)
#    #     print("*"*100)
#    #     print("URL: ", url)
#    #     print("*"*100)
#    #     pprint.pprint(data)
#    #     print("*"*100)
#    #     breakpoint()
#    #     time.sleep(5) # sleep 5 seconds between reqeusts
#    print(urls)
#    print("*"*100)
#print(output)
