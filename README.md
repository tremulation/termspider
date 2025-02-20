# termSpider
adaptable web crawler script for finding specified terms across a list of websites. 

## Installation
You need Python 3.6, and these libraries:
```bash
pip install requests beautifulsoup4
```

## Using the Script
In the main function, set your search terms and the sites to search.
```python
terms = ['term1', 'term2', ...]

base_urls = [
    "https://example.one.com",
    "https://example.two.com",
    ...
]
```
If you want to see context for each match printed out in the console, set debug to 'True'.

If you want this debug output to be saved to the output files, then set includeDebugWithOutput to "True" as well. 

run the script:
```bash
python termspider.py
```

## Notes
Adjust the filtering in get_page_content depending on the specific sites you're scraping from.

Do a couple test runs with max_pages set to 200, verify that you're filtering out everything you don't want, and then bump up max_pages to something very high, so you can traverse the whole site.
