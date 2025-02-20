import requests
from bs4 import BeautifulSoup, Comment
from bs4 import XMLParsedAsHTMLWarning
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import warnings
import re

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

def main():
    # add terms you want to search for here
    terms = ['term1', 'term2', 'term3', 'term4']

    # add websites to scrape here
    base_urls = [
        "https://example.one.com",
        "https://example.two.com"
    ]

    # enable debug to print out all the snippets that match the terms in the console
    # each different page will be separated with a bar of "-------"
    debug = True

    # include debug messages with output files.
    # When True, the output file will contain the full debug snippet
    # for every match instead of just the URL.
    includeDebugWithOutput = True

    # 100-500 is good for testing, but you should set it arbitrarily high
    #  when you run it for real, since you want to visit each page
    max_pages = 1000

    # dictionary mapping of keywords to all the urls (or debug text) that match
    keyword_to_urls = {term: [] for term in terms}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
    }
    
    # for each URL provided, crawl it and look for pages with matching content
    for base_url in base_urls:
        visited = set()
        urls_to_visit = {base_url}

        domain = urlparse(base_url).netloc
        while urls_to_visit and len(visited) < max_pages:
            url = urls_to_visit.pop()
            if url in visited:
                continue
            visited.add(url)
            try:
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code != 200:
                    continue
                # print out status message every 50th page visited
                if len(visited) % 50 == 0:
                    print(f"{len(visited)} pages visited on {domain}...")
                
                content = response.text

                # create soup object
                soup = BeautifulSoup(content, 'html.parser')

                # get clean page content w/out navigational headers/sidebars
                clean_page_content = get_page_content(soup)

                # new soup object with links intact for crawling
                link_soup = BeautifulSoup(content, 'html.parser')

                # check if page contains any of the terms:
                for term in terms:
                    if term.lower() in clean_page_content.lower():
                        if includeDebugWithOutput:
                            debug_text = get_debug_text(url, term, soup)
                            keyword_to_urls[term].append(debug_text)
                        else:
                            keyword_to_urls[term].append(url)
                        if debug:
                            debug_keyword_match(url, term, soup)

                # find all links on page
                for link in link_soup.find_all('a'):
                    href = link.get('href')
                    if not href:
                        continue

                    full_url = urljoin(url, href)
                    # Remove the fragment by setting it to an empty string
                    parsed_url = urlparse(full_url)
                    clean_url = parsed_url._replace(fragment="").geturl()

                    if urlparse(clean_url).netloc == domain and clean_url not in visited:
                        urls_to_visit.add(clean_url)

            except requests.exceptions.RequestException as e:
                print(f"Request error for {url}: {str(e)}")
                continue
            except Exception as e:
                print(f"Other error processing {url}: {str(e)}")
                continue

    # save results to txt files
    for term, results in keyword_to_urls.items():
        with open(f"{term}.txt", "w") as file:
            for result in results:
                file.write(result + "\n")
        print(f"Term '{term}' matched {len(results)} times.")

    total_matches = sum(len(results) for results in keyword_to_urls.values())
    print(f"Total matches across all terms: {total_matches}")



# this function gets the page content and cleans it up to remove headers and stuff
# you'll probably need to write your own filters to remove stuff like headers or
# other elements specific to your problem
# turning debugging on will help you see where your matches are, and where you,
# and how you need to write your filters
def get_page_content(soup):
    # create a copy so we don't modify the original soup used for link extraction
    content_soup = soup

    # remove ONE div with a certain id (and its content) 
    header_main = soup.find('div', id='ExampleClass')
    if header_main:
        header_main.decompose()

    # remove non-visible elements
    for element in content_soup(['script', 'style', 'meta', 'noscript', 'link', 'comment']):
        element.decompose()

    # remove elements that you can't see (hidden in CSS)
    for element in content_soup.find_all(style=re.compile(r'display:\s*none|visibility:\s*hidden')):
        element.decompose()
    
    # remove navigational elements
    for nav in content_soup.find_all(['nav', 'header', 'footer', 'aside', 'headerMain']):
        nav.decompose()

    # remove links
    for link in content_soup.find_all('a'):
        link.decompose()

    # get text content, normalize whitespace, and convert to lowercase
    return content_soup.get_text(separator=' ', strip=True).lower()



# prints out every match for one term on a page to the console 
def debug_keyword_match(url, term, soup):
    """
    Prints debug info for a match.
    """
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    matches = soup.find_all(string=pattern)

    if not matches:
        print(f"DEBUG: No direct text match for '{term}' in {url}")
        return

    for match in matches:
        print(f"MATCH:  for '{term}' in {url}")
        print(f"       Snippet: {match.strip()[:300]}...")
    print("-------------------------------------------------------------")



# returns a string with the debug info for a match, which you can write to a file
def get_debug_text(url, term, soup):
    """
    Returns a string with the debug info for a match.
    """
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    matches = soup.find_all(string=pattern)
    output_lines = []
    
    if not matches:
        output_lines.append(f"DEBUG: No direct text match for '{term}' in {url}")
    else:
        for match in matches:
            output_lines.append(f"MATCH:  for '{term}' in {url}")
            snippet = match.strip()[:300]
            output_lines.append(f"       Snippet: {snippet}...")
    output_lines.append("-------------------------------------------------------------")
    return "\n".join(output_lines)



if __name__ == "__main__":
    main()
