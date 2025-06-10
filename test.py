from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def mm_inference_openrouter(system_prompt, user_prompt, model, image_urls=None, max_tokens=25000, temperature=0.2):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    
    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    user_content = [{"type": "text", "text": user_prompt}]

    # Handle multiple images
    if image_urls:
        for url in image_urls:
            user_content.append({ "type": "image_url", "image_url": {"url": url} })

    messages.append({
        "role": "user",
        "content": user_content
    })

    try:
        completion = client.chat.completions.create(
            model=model, 
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        if completion and completion.choices and len(completion.choices) > 0:
            return completion.choices[0].message.content
        else:
            print("⚠️ No choices returned. Full response:")
            print(completion)
            return None

    except Exception as e:
        print("❌ API call failed:", e)
        return None




def get_image_urls_by_ids(json_path, selected_ids, require_valid=True):
    """
    Load image URLs from a JSON file based on a list of IDs.

    Args:
        json_path (str): Path to the JSON file.
        selected_ids (list of int): List of image IDs to extract.
        require_valid (bool): If True, only return images marked as valid_image=True.

    Returns:
        List of image URLs (strings).
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    image_urls = []
    for image in data.get("images", []):
        if image["id"] in selected_ids:
            if require_valid and not image.get("valid_image", False):
                continue
            image_urls.append(image["url"])
    
    return image_urls


"""
    Test adding qwen more than one images
"""

prompt= 'Describe those images'
path = "evidence_filtering/output.json"

# qwen/qwen2.5-vl-{72,32,3}b-instruct:free  qwen/qwen-2.5-vl-7b-instruct:free
response = mm_inference_openrouter(system_prompt="", user_prompt=prompt,model='qwen/qwen2.5-vl-32b-instruct:free', image_urls=get_image_urls_by_ids(path,[1,3,4,5,6,7,8,9]))

print("\nResponse:\n", response)



