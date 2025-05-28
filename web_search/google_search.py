import requests
import json
import os
from web_search.utils import scrape_multiple_urls, save_image_urls_from_links

from dotenv import load_dotenv
import os

load_dotenv()


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("CSE_ID")




def google_search_call(query, image_search, numResults):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'q': query,
        'key': GOOGLE_API_KEY,
        'cx': CSE_ID,
        'num': numResults,
    }
    if image_search:
        params["searchType"] = "image"

    response = requests.get(url, params=params)
    return response.json()



def search_and_scrap_results(parent_dir, query, queryID, isImageSearch,numResults):

    results = google_search_call(query,isImageSearch,numResults)

    print(f"\nGoogle Search results for '{query}':\n")
    for item in results['items']:
        print(item['title'], item['link'])


    if isImageSearch:
        print("\nSaving images...\n")
        save_image_urls_from_links(results['items'],queryID,parent_dir)
    else:
        print("\nScraping those results...\n")
        scrape_multiple_urls(results['items'],queryID,parent_dir)



def run_searches_from_query_file(entry_id, is_image_search=False, num_results=5):
    
    query_file_path = f"models/responses/{entry_id}_queries_version1.json"

    # Load search queries
    with open(query_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    queries = data.get("generated_queries", [])

    # Create dir
    entry_dir = f"web_search/{entry_id}"
    os.makedirs(entry_dir, exist_ok=True)

    for i, query in enumerate(queries):
        query_id = f"{entry_id}_q{i+1}_v1"  # e.g., "post123_q1"
        print(f"\n\n\n🔍 Running search for: {query} (Query ID: {query_id})")
        search_and_scrap_results(entry_dir, query, query_id, is_image_search, num_results)



#run_searches_from_query_file('mi5078')




"""
    Test a specific query
"""
"""
QUERY = "'Jackson Hinkle legal history"
QUERY_ID = "12testID34"
IMAGE_SEARCH = False
NUM_RESULTS = 6 # MAX 10
search_and_scrap_results(QUERY,QUERY_ID,IMAGE_SEARCH,NUM_RESULTS)
"""
