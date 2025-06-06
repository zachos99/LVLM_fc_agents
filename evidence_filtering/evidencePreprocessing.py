import xml.etree.ElementTree as ET
import json
import re
from PIL import Image
import requests
from io import BytesIO



def is_valid_image(url, min_width=100, min_height=100):
    """
    Checks if an image URL points to a valid image for analysis:
    --> Not small (based on dimensions)
    --> Doesn't contain undesirable keywords
    Returns:
        (is_valid, reason)
    """

    """
        Try to load the image and check dimensions
    """
    try:
        response = requests.get(url, timeout=10)
        img = Image.open(BytesIO(response.content))
        width, height = img.size
        if width < min_width or height < min_height:
            return False, "Filtered by size"
    except Exception as e:
        return False, f"Failed to load image ({str(e)})"


    """
        Than also apply keyword filtering (low chance of being useful)

        ?? Should I do it ? ??
    """
    bad_keywords = ["favicon", "sprite", "spacer", "tracking", "logo", "icon", "banner"]

    if any(kw in url.lower() for kw in bad_keywords):
        return False, "Filtered by keyword"
    
    # Otherwise image is valid
    return True, None
    



def readable_print_for_debugging(text):
    """
        Save content in an a readable format for debugging
        Adds newlines between tags and markers to improve readability of cleaned HTML/XML-like text.
    """
    # Add newline after each closing tag, before each opening tag and before/after [image x] markers
    text = re.sub(r'(</[^>]+>)', r'\1\n', text)
    text = re.sub(r'(?<!\n)(<[^/][^>]*>)', r'\n\1', text)
    text = re.sub(r'(\[image \d+\])', r'\n\1\n', text)

    # Remove excessive blank lines
    lines = [line.strip() for line in text.split('\n')]
    pretty_text= "\n".join(line for line in lines if line)
    with open("evidence_filtering/output_debug.xml", "w", encoding="utf-8") as f:
        f.write(pretty_text)





def clean_graphic_tags(main_elem, image_urls):
    """
    Replaces <graphic> tags with [image id] markers using known image URLs.
    """
    image_url_map = {img["url"]: img["id"] for img in image_urls}

    # Convert <main> element to string
    main_str = ET.tostring(main_elem, encoding='unicode')   

    def replace_graphic(match):
        src = match.group(1)
        matched_id = None
        for url, img_id in image_url_map.items():
            if url.endswith(src):  # Match by suffix
                matched_id = img_id
                break
        return f"[image {matched_id}]" if matched_id else ""

    # Replace <graphic src="..."/> with [image id]
    pattern = r'<graphic\s+[^>]*src="([^"]+)"[^>]*/>'
    cleaned_main = re.sub(pattern, replace_graphic, main_str)


    return cleaned_main






def process_evidence(xml_path, image_json_path):
    # Load and parse XML
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        return {"valid": False, "reason": f"XML parsing failed: {e}"}
    

    metadata = dict(root.attrib)  # Dynamically include all available <doc> attributes


    # We keep only the <main> content ignoring other parts like <comments>
    main = root.find("main")
    if main is None:
        print("Removed evidence -no <main> found!")
        return {"valid": False, "reason": "No <main> content found", "metadata": metadata}
    
       
    # Load image list from JSON
    try:
        with open(image_json_path, 'r') as f:
            images = json.load(f)
    except Exception as e:
        print("Image JSON loading failed!")
        return {"valid": False, "reason": f"Image JSON loading failed: {e}", "metadata": metadata}
    
     # Map each image URL to an ID
    image_url_map = {}
    image_urls = []
    for idx, image in enumerate(images, start=1):
        url = image.get("image_url", {}).get("url")
        source_url = image.get("source_url")

        if not url:
            continue
            
        is_valid, reason = is_valid_image(url)

        image_url_map[url] = idx

        image_urls.append({
            "id": idx,
            "url": url,
            "source_url": source_url,
            "valid_image": is_valid,
            "reason": reason
        })

    # Replaces <graphic> tags with [image id] markers
    cleaned_main_text = clean_graphic_tags(main, image_urls)

    # Check for Text Length
    if len(cleaned_main_text.strip()) < 300:
        print("Removed evidence due to length!")
        return {"valid": False, "reason": "Too little meaningful text", "metadata": metadata}
    

    # Should also add filtering/warning for scraping cookies policies or 'enable Javascript' errors? 

    return {
        "valid_evidence": True,
        "metadata": metadata,
        "text": cleaned_main_text,
        "images": image_urls
    }



