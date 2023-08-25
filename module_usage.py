import requests
import pprint
import time
import json
from foolcalls.scrapers import scrape_transcript_urls_by_page, scrape_transcript

# # get one transcript for a known url
# transcript_url = 'https://www.fool.com/investing/2023/08/25/why-vinfast-auto-jumped-again-today/'
# response = requests.get(transcript_url)
# transcript = scrape_transcript(response.text)

# get all (~20) transcript urls from a single page
# transcript_urls = scrape_transcript_urls_by_page(page_num=1)
# print(transcript_urls)

# combine the two above to get a handful of transcripts from fool.com
num_of_pages = 3 # will be ~60 transcripts, with ~20 transcript urls per page
output = []
for page in range(0, num_of_pages):
    urls = scrape_transcript_urls_by_page(page)
    for url in urls:
        response = requests.get(url)
        data = scrape_transcript(response.text)
        output.append(url)
        print("*"*100)
        print("URL: ", url)
        print("*"*100)
        pprint.pprint(data)
        print("*"*100)
        breakpoint()
        time.sleep(5) # sleep 5 seconds between reqeusts
print(output)