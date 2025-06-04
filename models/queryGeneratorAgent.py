import json

from datetime import datetime

from models.togetherai import mm_inference_togetherai 
from models.openrouter import mm_inference_openrouter

from models.utils import load_post_analysis, extract_and_save_queries, remove_think_block



def build_query_generator_system_prompt():
    today_date = datetime.today().strftime('%B %d, %Y') 

    return (
        f"""You are a search assistant helping fact-checking agents investigate online claims. Today's date is {today_date}. Your job is to generate effective and diverse web search queries that could help verify a multimodal social media post. The goal is to surface useful evidence or contextual information — not to confirm or deny the post outright. Queries should reflect the key elements of the post, including people, events, objects, locations, or visuals, and help retrieve factual or verifiable online content. Some queries may focus on textual evidence like news coverage, official mentions, or public reports. Others may focus on image-related evidence such as similar photos, object identification, or reverse-image-style searches. Do not include overly generic or emotional phrases like "is this real" or "fact check." Each query should be precise, realistic, and useful for investigation."""
    )

def build_query_generator_user_prompt(post_text, structured, num_queries):
    return f"""
Here is a social media post:

--- POST TEXT ---
{post_text}
-----------------

Below is the structured analysis of the post:
- Named Entities: {structured.get("named_entities", [])}
- Who: {structured.get("five_ws", {}).get("who", "Unclear")}
- What: {structured.get("five_ws", {}).get("what", "Unclear")}
- Where: {structured.get("five_ws", {}).get("where", "Unclear")}
- When: {structured.get("five_ws", {}).get("when", "Unclear")}
- Why: {structured.get("five_ws", {}).get("why", "Unclear")}
- Image Description: {structured.get("image_description", "Unclear")}
- OCR Text: {structured.get("ocr_text", "None")}
- Manipulation Signs: {structured.get("manipulation_signs", "Unclear")}
- Emotive Language: {structured.get("emotive_or_fallacious_language", "None")}
- Timestamp Notes: {structured.get("timestamp_consistency", "None")}

Your task: Based on this information, generate optimized diverse search-engine ready queries to help gather useful evidence or context for the post. Give me {num_queries} for text and 1 for image search.
For image-related queries:
- If the image shows a specific person, place, or event that is named in the post, include that name in the image search query (e.g. "Elon Musk Cybertruck photo").
- Only use visual descriptions (e.g. "man in suit") if the identity is unknown.
- Prioritize queries that help visually confirm or refute the post, such as comparing two identities, locations, or known images of the subject.
Important: Return a list of JSON objects, each containing:
- "query": a search string
- "search_type": either "text" or "image"
Do not include any explanations, formatting, or labels — just return the JSON list.
"""


def queryGeneratorAgent(entry_id, platform, model, num_queries, **kwargs):
    post_analyzer_response = load_post_analysis(entry_id)

    system_prompt = build_query_generator_system_prompt()

    user_prompt = build_query_generator_user_prompt(
        post_text=post_analyzer_response["post_text"],
        structured=post_analyzer_response["structured_response"], 
        num_queries=num_queries
    )

    print(f"Asking {model}...")
    

    if(platform=='openrouter'):
        print("Using OpenRouter API...\n")
        response = mm_inference_openrouter(system_prompt,user_prompt,model,**kwargs)
    elif(platform=='togetherai'):
        print("Using TogetherAI API...\n")
        response = mm_inference_togetherai(system_prompt,user_prompt,model,**kwargs)
        if "deepseek" in model.lower():
            response = remove_think_block(response)
    else:
        print('Please enter a valid AI platform!')
        return
 
    print(response)


    extract_and_save_queries(response, entry_id)

