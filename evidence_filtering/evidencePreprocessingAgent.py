import json
import os

from evidence_filtering.evidencePreprocessingUtils import process_evidence, is_valid_image,readable_print_for_debugging



"""
        Given an entryID, agent parses every scraped search result 
"""

"""
    If we want to test the agent, we can print <main> in an a readable format for debugging
        xml_path = "web_search/ma2975/ma2975_q2_v1/ma2975_q2_v1_result_1.xml"
        images_path = "web_search/ma2975/ma2975_q2_v1/ma2975_q2_v1_result_1_scrapedImageURLs.json"
        processed_evidence = process_evidence(xml_path,images_path)
        readable_print_for_debugging(processed_evidence.get('text'))
"""


def process_entry_evidence(entry_id, base_input_dir="web_search", base_output_dir="evidence_filtering/evidencePreprocessing"):

    input_root = os.path.join(base_input_dir, entry_id)
    output_root = os.path.join(base_output_dir, entry_id)
    os.makedirs(output_root, exist_ok=True)

    for subfolder in os.listdir(input_root):
        subfolder_path = os.path.join(input_root, subfolder)
        if not os.path.isdir(subfolder_path):
            continue

        # files contains every xml and json file from the subfolders
        files = os.listdir(subfolder_path)
        

        
        # Check if query folder is a text or an image query
        # If it is text query then identify the scraped page(xml)-scraped images(json) pairs
        # Then for each pair run the preprocessing and save the result  
        xml_files = [f for f in files if f.endswith(".xml")]
        for xml_file in xml_files:
            base_name = xml_file.replace(".xml", "")
            json_file = f"{base_name}_scrapedImageURLs.json"

            xml_path = os.path.join(subfolder_path, xml_file)
            json_path = os.path.join(subfolder_path, json_file)

            if os.path.exists(json_path):
                print(f"Processing text query pair: {xml_file} + {json_file}")
                try:
                    processed = process_evidence(xml_path, json_path)
                    output_file = os.path.join(output_root, f"{base_name}.json")
                    
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(processed, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"Error processing {xml_file}: {e}")
            else:
                print(f"Missing JSON pair for: {xml_file}")

        # For image queries we just add the validity and reason
        image_jsons = [f for f in files if f.endswith("_googleSearchImageURLs.json")]
        for img_file in image_jsons:
            img_path = os.path.join(subfolder_path, img_file)
            print(f"Processing image query: {img_file}")

            try:
                with open(img_path, "r", encoding="utf-8") as f:
                    image_entries = json.load(f)

                if not isinstance(image_entries, list):
                    print(f"⚠️ Skipping {img_file} (unexpected format)")
                    continue

                for entry in image_entries:
                    url = entry.get("image_url", {}).get("url")
                    if url:
                        is_valid, reason = is_valid_image(url)
                        entry["is_valid"] = is_valid
                        entry["reason"] = reason
                    else:
                        entry["is_valid"] = False
                        entry["reason"] = "Missing URL"

                # Save enriched entries
                base_name = img_file.replace(".json", "")
                output_file = os.path.join(output_root, f"{base_name}.json")
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(image_entries, f, ensure_ascii=False, indent=2)

            except Exception as e:
                print(f"Error processing image query {img_file}: {e}")



