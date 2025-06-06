import requests
import random

from dotenv import load_dotenv
import os

from search_engines import Google, http_client
from duckduckgo_search import DDGS

from web_search.utils import build_excluded_query

load_dotenv()


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("CSE_ID")

# Domains to exclude from search
# "reddit.com" ??
BLOCKED_DOMAINS = ["facebook.com", "instagram.com", "pinterest.com", "youtube.com", "x.com", "flickr.com","reddit.com"]



def google_search_call(base_query, image_search, numResults):
    url = 'https://www.googleapis.com/customsearch/v1'
  
    # Build query for domain exclusion
    query = build_excluded_query(base_query, BLOCKED_DOMAINS)

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



def duckduckgo_scraping_call(base_query, num_results, isImageSearch=False):
    """
        Check DDG Documentation for more utilities !!!!
    """

    query = build_excluded_query(base_query, BLOCKED_DOMAINS)

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
    }

    formatted_results = []
        
    # Can also add proxy="tb" --> "tb" is an alias for "socks5://127.0.0.1:9150"
    with DDGS(headers=headers, timeout=10) as ddgs:
        if isImageSearch:
            results = ddgs.images(query, max_results=num_results)
            for item in results:
                formatted_results.append({
                    "title": item.get("title", ""),
                    "link": item.get("image", "")
                })
        else:
            results = ddgs.text(query, max_results=num_results)
            for item in results:
                formatted_results.append({
                    "title": item.get("title", ""),
                    "link": item.get("href", "")
                })
    
    return {
        "items": formatted_results
    }



def serp_scraping_call(query, num_results):

    # Add website exceptions to the query and search Google
    search_query = build_excluded_query(query, BLOCKED_DOMAINS)

    engine = Google()
    print("\n~~~~~~~~~~~~~~~~~~\nQuery is:",query,"\n~~~~~~~~~~~~~~~~~~\n\n")

    print("Waiting a bit...")
    engine._delay = random.uniform(10, 20)
    engine._http_client = http_client.HttpClient() # Fresh session clears cookies
    engine.set_headers({'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"})
    
    # 🔎 Proceed with real search (may error if blocked)
    try:
        results = engine.search(search_query, pages=1)
        return {"items": results[:num_results]}
    except Exception as e:
        print(f"❌ SERP scraping failed: {e}")
        return {"items": []}

    
    

