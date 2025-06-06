import json
import os

#web_search.
from web_search.utils import scrape_multiple_urls, save_image_urls_from_links
from web_search.search_methods import google_search_call, duckduckgo_scraping_call,serp_scraping_call



def search_and_scrap_results(parent_dir, query, queryID, numResults, isImageSearch=False):

    ########################################################################
    # REPLACE IT WITH ANOTHER FUNCTION WHEN WE WILL ADD DIFFERENT ENGINES #
    #######################################################################
    api_mode = "Google"

    if(api_mode=="Google"):
        print('\nGoogle API Mode...\n')
        results = google_search_call(query,isImageSearch,numResults)
    elif (api_mode=='DDG'):
        ## Searching with duckduckgo-search py library
        print('\nDuckDuckGo Mode...\n')
        results  = duckduckgo_scraping_call(query,numResults, isImageSearch)
    elif(api_mode=="SERP"):
        ## SERP scraping with git repo
        print('\nSERP Scraping Mode...\n')
        results = serp_scraping_call(query,numResults)
    else:
        print("Please enter a valid search mode!")


    print(f"\nSearch results for '{query}':\n")
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

    for i, query_obj in enumerate(queries):
        query_text = query_obj.get("query")
        search_type = query_obj.get("search_type", "text").lower()

        if not query_text:
            continue  # skip malformed entries

        is_image_search = (search_type == "image")

        query_id = f"{entry_id}_q{i+1}_v1" # e.g., "post123_q1"
        print(f"\n\n\n🔍 Running {search_type} search for: {query_text} (Query ID: {query_id})")

        search_and_scrap_results(entry_dir, query_text, query_id, num_results, is_image_search)











"""
    Test a specific query
        (remove web_search. from imports if running inside web_search folder)
"""
"""  
QUERY = "International Space Station reflection in helmet visor images"
QUERY_ID = "12testID34"
IMAGE_SEARCH = False
NUM_RESULTS = 5 # MAX 10

search_and_scrap_results("./web_search",QUERY,QUERY_ID,NUM_RESULTS, IMAGE_SEARCH)
"""