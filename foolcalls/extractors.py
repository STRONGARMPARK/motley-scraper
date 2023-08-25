import re
from lxml import html
import logging
from foolcalls.decorators import handle_many_elements, handle_one_element
import datetime

log = logging.getLogger(__name__)

# extract the links
@handle_many_elements(error_on_empty=False)
def get_call_urls(html_selector):
    call_urls = html_selector.xpath('.//div[@class = "page" and @data-pagenum = "1"]'
                                    '//div[@class="flex py-12px text-gray-1100"]/a/@href')
    return call_urls

@handle_one_element(error_on_empty=True)
def find(parent_element, xpath_str):
    return parent_element.xpath(xpath_str)


@handle_many_elements(error_on_empty=True)
def findall(parent_element, xpath_str, concat_results=False):
    elements = parent_element.xpath(xpath_str)
    if concat_results:
        return html.fromstring(b''.join([html.tostring(el) for el in elements]))
    return elements

# returns unix timestamp
def extract_date(date_str):
    # Assuming date is a string containing the date
    match = re.search(r'([A-Z][a-z]{2,3}) ([0-9]{1,2}), ([0-9]{4}) at ([0-9]{1,2}:[0-9]{1,2}[A-Z]*)', date_str)

    # Extract the date components from the match
    month = match.group(1)
    day = match.group(2)
    year = match.group(3)
    time = match.group(4)

    # Assuming month, day, year, and time are extracted from the date string
    date_str = f'{month} {day} {year} {time}'
    date_obj = datetime.datetime.strptime(date_str, '%b %d %Y %I:%M%p')
    unix_timestamp = int(date_obj.timestamp())

    # Print the Unix timestamp
    return unix_timestamp

def extract_body(body_lst, author):
    body = ""
    for section in body_lst:
        body += section.text_content()
    # Find all occurrences of the author name in the article text

    # Assuming body is a string containing the article body and author is a string containing the author name
    author_lower = author.lower()

    # Find the approximate start and end of the article based on the first and second occurrences of the author name
    start_index = body.lower().find(author_lower)
    end_index = body.lower().find(author_lower, start_index + 1)

    return body[start_index:end_index]


def extract_author(date_str):
    match = re.search(r'.*By ([A-Z][a-z]* [A-Z][a-z]*).*', date_str) 
    author = match.group(1)
    return author

   
def extract_elements(html_text):
    html_doc = html.fromstring(html_text)

    article_header = find(parent_element=html_doc,
                          xpath_str='.//h1[contains(@class, "font-medium") and contains(@class, "text-gray-1100")]').text_content()

    #TODO get multiple tickers
    ticker = find(parent_element=html_doc,
                  xpath_str='.//a[contains(@class, "text-cyan-800") and contains(@class, "hover:text-cyan-700")]').text_content()

    date = find(parent_element=html_doc,
                xpath_str='.//div[contains(@class, "text-lg") and contains(@class, "font-medium") and contains(@class, "text-gray-800")]').text_content()

    author = extract_author(date)

    date = extract_date(date)
    
    body = findall(parent_element=html_doc,
                        xpath_str='.//div[contains(@class, "mx-auto") and contains(@class, "md:max-w-880") and contains(@class, "lg:max-w-1280")]')

    body = extract_body(body, author)

    elements = {'html_doc': html_doc,
                'article_header': article_header,
                'ticker': ticker,
                'date': date,
                'article_body': body}

    return elements