import pandas as pd
from duckduckgo_search import DDGS
import requests
import json
from bs4 import BeautifulSoup

from search_engines import Google, Yahoo



"""
    Search in any search Engine with this git repo
    https://github.com/tasos-py/Search-Engines-Scraper
"""
""" """
engine = Yahoo()
results = engine.search("Python Lang", pages=1)




data = []
for item in results:
    data.append({
        "title": item["title"],
        "link": item["link"],
        "text": item["text"],
        "host": item["host"]
    })


with open("results.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


