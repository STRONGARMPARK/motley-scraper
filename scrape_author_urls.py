from foolcalls.scrapers import scrape_author_article_urls_by_page
import time
import csv

def load_existing_authors():
    """Load existing authors from the CSV into a set."""
    authors = set()
    with open('output.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header
        for row in reader:
            if row:
                authors.add(row[0])
    return authors

# Check if the file exists and if not, create it with headers
try:
    with open('output.csv', 'r') as f:
        pass
except FileNotFoundError:
    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Author", "Article URL"])

# Load existing authors into a set
existing_authors = load_existing_authors()

print(existing_authors)

# iterate through all 4 digit numbers
for i in range(1, 25000):
    print("*"*100)
    zeros = 5 - len(str(i))
    author = "0" * zeros + str(i) 
    # Check if the author already exists in the set
    if author in existing_authors:
        print(f"Author {author} already exists in the CSV. Skipping...")
        continue
    article_urls = []
    page = 1
    while True:
        links = scrape_author_article_urls_by_page(page, author)
        if len(links) == 0:
            break
        for link in links:
            article_urls.append([author, link])
        print("Reading page: ", page)
        page += 1
        time.sleep(5)
    print("Done collecting links for author: ", author)
    print("Adding {} links to the CSV".format(len(article_urls)))
    # open a CSV file for writing
    with open('output.csv', 'a', newline='') as csvfile:
        # create a CSV writer object
        writer = csv.writer(csvfile)

        # write each row to the CSV file
        for row in article_urls:
            writer.writerow(row)
