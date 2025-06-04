
import json
import random

from search_engines import Google, http_client


from web_search.utils import build_excluded_query
from web_search.google_search import search_and_scrap_results



"""
    Search in any search Engine with this git repo
    https://github.com/tasos-py/Search-Engines-Scraper
"""


def serp_scraping_call(query, num_results):

    # Add website exceptions to the query and search Google
    search_query = build_excluded_query(query, BLOCKED_DOMAINS)

    engine = Google()

    print("\n~~~~~~~~~~~~~~~~~~\nQuery is:",query,"\n~~~~~~~~~~~~~~~~~~\n\n")

    print("Waiting a bit...")
    engine._delay = random.uniform(10, 20)
    engine._http_client = http_client.HttpClient() # Fresh session clears cookies
    engine._headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

    
    results = engine.search(search_query, pages=1)

    return {
        "items": results[:num_results]
    }


"""
def search_and_scrap_results(parent_dir, query, queryID, numResults, isImageSearch=False):

    results = search_and_save(query,numResults)

    print(f"\nGoogle Search results for '{query}':\n")
    for item in results['items']:
        print(item['title'], item['link'])


    if isImageSearch:
        print("\nSaving images...\n")
        save_image_urls_from_links(results['items'],queryID,parent_dir)
    else:
        print("\nScraping those results...\n")
        scrape_multiple_urls(results['items'],queryID,parent_dir)
"""


