import pandas as pd
import requests
import os
import re
import json
from datetime import datetime
from urllib.parse import urljoin

import trafilatura
from trafilatura.downloads import fetch_url

from playwright.sync_api import sync_playwright


def extract_and_fix_image_urls(xml_response, base_url):
    """
    Extracts all image URLs from a Trafilatura XML response and resolves relative URLs.
    Returns a list of absolute image URLs.
    """

    if not isinstance(xml_response, str):
        return []
    
    
    # Find all image src attributes using regex
    img_srcs = re.findall(r'src="([^"]+)"', xml_response)
    
    full_urls = []

    for src in img_srcs:
        if src.startswith("http"):
            full_urls.append(src)
        else:
            # Fix relative URLs
            full_urls.append(urljoin(base_url, src))

    return full_urls


def fetch_dynamic_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # --> Set false for debugging
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9"
            },
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        try:
            page.goto(url, timeout=60000)
        except Exception as e:
            print(f"❌ Couldn't scrape: {url}\nReason: {e}")
            return None, []

        #################################
        ## TO DISMISS COOKIES BANNERS ##
        ###############################
        cookie_texts = [
       "Accept", "Continue", "Agree", "OK", "I agree", "AGREE", "Consent",
       "Allow all", "Allow all cookies", "Accept all", "Accept all cookies",
       "Accept All", "Accept all" "Agree & continue", "Accept cookies"]   
        
        # Build a combined selector
        selector = ", ".join([f"button:has-text('{text}')" for text in cookie_texts])

        try:
            button = page.locator(selector).first
            button.click(timeout=1500)
            print("Clicked a cookie consent button!")
        except:
            print("")


        page.wait_for_timeout(5000)  # Wait 5s for JS to load

        #page.screenshot(path="screenshot.png", full_page=True)
        html = page.content()
        browser.close()
        return html


def scrape_url(url):
    
    # Fetch using requests lib 
    #headers = {'User-Agent': 'Mozilla/5.0'}
    #html = requests.get(url, headers=headers).text
   
    # Fetch using trafilatura
    #html = fetch_url(url)

    # Fetch using playwright
    html = fetch_dynamic_html(url)


    result = trafilatura.extract(html, output_format="xml", with_metadata=True, include_tables=True, include_images=True)

    if result is None:
        print(f"⚠️ Failed to extract from {url}")
        return None, []

    image_url_list = extract_and_fix_image_urls(result,url)


    return result , image_url_list





def scrape_multiple_urls(items,query_id,parent_dir):
    all_results = []
    all_image_lists = []

    save_dir = f"{parent_dir}/{query_id}"#_search_results"
    os.makedirs(save_dir, exist_ok=True)


    for i, item in enumerate(items):

        url = item.get("link", "")
        title = item.get("title", "")

        result, image_list = scrape_url(url)

        if result is None:
            continue

        all_results.append(result)
        all_image_lists.append(image_list)

        # Save XML result
        with open(f"{save_dir}/{query_id}_result_{i}.xml", "w", encoding="utf-8") as f:
            f.write(result)

        # Save image URLs
        formatted_images = [{
            "title": title,
            "source_url": url,
            "type": "image_url",
            "image_url": {"url": img}
        } for img in image_list]

        with open(f"{save_dir}/{query_id}_result_{i}_scrapedImageURLs.json", "w", encoding="utf-8") as f:
            json.dump(formatted_images, f, indent=2, ensure_ascii=False)

        print(f"Saved results for URL: {url}")

    return all_results, all_image_lists




def save_image_urls_from_links(items, query_id,parent_dir):
    save_dir = f"{parent_dir}/{query_id}"
    os.makedirs(save_dir, exist_ok=True)

    all_images_info = []

    #for i,img_url in enumerate(links):
    #    formatted = {"type": "image_url", "image_url": {"url": img_url}}
    #    all_formatted_images.append(formatted)

    for item in items:
        image_info = {
            "title": item.get("title", ""),
            "type": "image_url",
            "image_url": {
                "url": item.get("link", "")
            }
        }
        all_images_info.append(image_info)



    # Save all together in one file too
    with open(f"{save_dir}/{query_id}_googleSearchImageURLs.json", "w", encoding="utf-8") as f:
        json.dump(all_images_info, f, indent=2, ensure_ascii=False)

    return all_images_info





def build_excluded_query(base_query, blocked_domains):
    """
        Takes as input an array of blocked domains of Google Search 
        and formats the query for the API 
    """
    exclusions = " ".join([f"-site:{domain}" for domain in blocked_domains])
    return f"{base_query} {exclusions}".strip()
