import pandas as pd
import requests
import os
import re
import json
from datetime import datetime

from dotenv import load_dotenv
import os

load_dotenv()


IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")


def format_timestamp(timestamp):
    """
        Takes a timestamp and returns it in a readable format
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%d %B %Y")
    except ValueError:
        return "Invalid timestamp"
   
   
def get_entry_info(uniqueID):
    """
        Given a uniqueID this functions returns information from dataset
    """

    df = pd.read_csv("mm_data/dataset.csv")  
    
    row = df[df['uniqueID'] == uniqueID]
    
    if row.empty:
        print(f"No entry found for uniqueID: {uniqueID}")
        return None

    tweet_text = row.iloc[0].get('tweetText', '')
    note_text = row.iloc[0].get('noteText', '')
    
    media_files_str = row.iloc[0].get('tweetMediaFiles', '')
    media_files = media_files_str.split(',') if pd.notna(media_files_str) else []

    tweet_date = row.iloc[0].get('tweetCreatedAt', '')
    
    return {
        "tweetText": tweet_text,
        "noteText": note_text,
        "tweetMediaFiles": media_files,
        "tweetCreatedAt": tweet_date
    }



def upload_to_imgbb(path):
    """ 
        Converts a local Image into a URL by uploading to imgbb 
    """

    base_path = "mm_data/twikit/images"
    image_path = os.path.join(base_path, path)

    # Some images are png but mistakenly are saved as jpg in dataset column
    if not os.path.exists(image_path) and path.endswith(".jpg"):
        path = path.replace(".jpg", ".png")
        image_path = os.path.join(base_path, path)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(image_path, "rb") as f:
        res = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": IMGBB_API_KEY, 
                  "expiration": 3600  }, # Auto-delete after 1 hour
            files={"image": f}
        )
    data = res.json()
    return data["data"]["url"]


def parse_response(response):
    """
    Parse LVLM response and extract structured data.
    
    Args:
        response (str): The raw LVLM response text
        
    Returns:
        Dict[str, Any]: Structured data dictionary
    """
    
    # Initialize the structured data dictionary
    structured_data = {
        "image_description": "",
        "ocr_text": "",
        "manipulation_signs": "",
        "named_entities": [],
        "five_ws": {
            "who": "",
            "what": "",
            "where": "",
            "when": "",
            "why": ""
        },
        "image_text_alignment": "",
        "emotive_or_fallacious_language": "",
        "timestamp_consistency": ""
    }
    
    # Helper function to extract content after a section header
    def extract_section_content(pattern,text):
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            # Remove leading "**" and trailing content after next "**" or "-"
            content = re.sub(r'^\*\*.*?\*\*:?\s*', '', content)
            # Stop at next section (starting with "- **" or end of string)
            next_section = re.search(r'\n- \*\*', content)
            if next_section:
                content = content[:next_section.start()].strip()
            return content
        return ""
    
    # Extract Image Description
    structured_data["image_description"] = extract_section_content(
        r'- \*\*Image Description\*\*:?\s*(.*?)(?=\n- \*\*|\Z)', response
    )
    
    # Extract OCR text
    ocr_content = extract_section_content(
        r'- \*\*OCR\*\*:?\s*(.*?)(?=\n- \*\*|\Z)', response
    )
    structured_data["ocr_text"] = ocr_content if ocr_content.lower() != "no visible text." else ""
    
    # Extract Manipulation Signs
    structured_data["manipulation_signs"] = extract_section_content(
        r'- \*\*Manipulation Signs\*\*:?\s*(.*?)(?=\n- \*\*|\Z)', response
    )
    
    # Extract Named Entities
    entities_content = extract_section_content(
        r'- \*\*Named Entities\*\*:?\s*(.*?)(?=\n- \*\*|\Z)', response
    )
    if entities_content:
        # Split by comma and clean up
        entities = [entity.strip().rstrip('.') for entity in entities_content.split(',')]
        structured_data["named_entities"] = entities
    
    # Extract 5Ws
    five_ws_section = re.search(r'- \*\*5Ws Extraction\*\*:?\s*(.*?)(?=\n- \*\*|\Z)', response, re.IGNORECASE | re.DOTALL)
    if five_ws_section:
        five_ws_content = five_ws_section.group(1)
        
        # Extract each W
        who_match = re.search(r'- \*\*Who.*?\*\*:?\s*(.*?)(?=\n\s*- \*\*|\Z)', five_ws_content, re.IGNORECASE | re.DOTALL)
        if who_match:
            structured_data["five_ws"]["who"] = who_match.group(1).strip().rstrip('.')
            
        what_match = re.search(r'- \*\*What.*?\*\*:?\s*(.*?)(?=\n\s*- \*\*|\Z)', five_ws_content, re.IGNORECASE | re.DOTALL)
        if what_match:
            structured_data["five_ws"]["what"] = what_match.group(1).strip().rstrip('.')
            
        where_match = re.search(r'- \*\*Where.*?\*\*:?\s*(.*?)(?=\n\s*- \*\*|\Z)', five_ws_content, re.IGNORECASE | re.DOTALL)
        if where_match:
            structured_data["five_ws"]["where"] = where_match.group(1).strip().rstrip('.')
            
        when_match = re.search(r'- \*\*When.*?\*\*:?\s*(.*?)(?=\n\s*- \*\*|\Z)', five_ws_content, re.IGNORECASE | re.DOTALL)
        if when_match:
            structured_data["five_ws"]["when"] = when_match.group(1).strip().rstrip('.')
            
        why_match = re.search(r'- \*\*Why.*?\*\*:?\s*(.*?)(?=\n\s*- \*\*|\Z)', five_ws_content, re.IGNORECASE | re.DOTALL)
        if why_match:
            structured_data["five_ws"]["why"] = why_match.group(1).strip().rstrip('.')
    
    # Extract Image-Text Alignment
    structured_data["image_text_alignment"] = extract_section_content(
        r'- \*\*Image-Text Alignment\*\*:?\s*(.*?)(?=\n- \*\*|\Z)', response
    )
    
    # Extract Emotive Language or Logical Fallacies
    structured_data["emotive_or_fallacious_language"] = extract_section_content(
        r'- \*\*Emotive Language or Logical Fallacies\*\*:?\s*(.*?)(?=\n- \*\*|\Z)', response
    )
    
    # Extract Timestamp Consistency Check
    structured_data["timestamp_consistency"] = extract_section_content(
        r'- \*\*Timestamp Consistency Check\*\*:?\s*(.*?)(?=\n- \*\*|\Z)', response
    )
    
    return structured_data


def save_response_to_json(tweet_text,image_path,response, entry_id):

    
    os.makedirs("models/responses", exist_ok=True)

    filepath = f"models/responses/{entry_id}_response.json"

    structured_response = parse_response(response)

    data = {
    "post_text": tweet_text,
    "image_url": image_path,
    "structured_response": structured_response,
    "raw_response": response
}
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)




def load_post_analysis(entry_id):

    filepath = f"models/responses/{entry_id}_response.json"
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return {
        "post_text": data.get("post_text", ""),
        "structured_response": data.get("structured_response", {})
    }



def extract_and_save_queries(text,entry_id, version="version1"):
    """
    Extracts search queries from an LLM-generated text.
    Assumes the model outputs a JSON list of objects with 'query' and 'search_type'.
    Saves it in JSON file
    """

    try:
        # Try to parse as JSON directly
        queries = json.loads(text)

        # Validate structure
        structured_queries = []
        for item in queries:
            if isinstance(item, dict) and "query" in item and "search_type" in item:
                structured_queries.append({
                    "query": item["query"].strip(),
                    "search_type": item["search_type"].strip().lower()
                })

    except Exception:
        print("⚠️ Could not parse structured JSON. Falling back to line-by-line parsing.")

        # Fallback: parse unstructured list (bullets or lines)
        lines = text.strip().splitlines()
        structured_queries = []

        for line in lines:
            cleaned = re.sub(r'^[\s\*\-•\d\.\)]+', '', line).strip()
            match = re.search(r'"([^"]+)"', cleaned)
            query = match.group(1).strip() if match else cleaned

            if len(query.split()) >= 3:
                structured_queries.append({
                    "query": query,
                    "search_type": "text"  # default fallback type
                })

    # We add 'version1' for now in case we want to extract extra queries later
    filepath = f"models/responses/{entry_id}_queries_{version}.json"

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({"generated_queries": structured_queries}, f, ensure_ascii=False, indent=2)




def remove_think_block(response_text):
    """
    Remove <think>...</think> block from the response of Deepseek
    """
    return re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL).strip()