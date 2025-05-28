import json

from datetime import datetime

from models.togetherai import mm_inference_togetherai 
from models.openrouter import mm_inference_openrouter

from models.utils import load_post_analysis, extract_and_save_queries



def build_query_generator_system_prompt():
    today_date = datetime.today().strftime('%B %d, %Y') 

    return (
        f"You are a search assistant helping fact-checking agents investigate online claims. Today's date is {today_date}. "
        "Your job is to generate 2–4 focused and effective web search queries that could help verify a social media post. "
        "Use named entities, events, dates, and context. Avoid emotionally charged or exaggerated phrases unless they are essential to the claim being checked. "
        "Prioritize queries that would return news articles, official statements, or social media coverage."
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

Now, generate {num_queries} optimized search queries (search-engine ready, in bullet list format) that would help an investigator find evidence online to support or refute the post's claims.
Be specific and realistic — use key people, events, and dates, and aim for relevance to current or recent events.
 Important: Return only a list of plain-text search queries. Do not include explanations, site filters, or extra formatting like bold text or numbering. Each line should be a self-contained query suitable for Google search.
"""




def queryGeneratorAgent(entry_id, platform, model, num_queries):
    post_analyzer_response = load_post_analysis(entry_id)

    system_prompt = build_query_generator_system_prompt()

    user_prompt = build_query_generator_user_prompt(
        post_text=post_analyzer_response["post_text"],
        structured=post_analyzer_response["structured_response"], 
        num_queries=num_queries
    )

    print(f"\nAsking {model}...\n")
    

    if(platform=='openrouter'):
        print("\nUsing OpenRouter API...\n")
        response = mm_inference_openrouter(system_prompt,user_prompt,model)
    elif(platform=='togetherai'):
        print("\nUsing TogetherAI API...\n")
        response = mm_inference_togetherai(system_prompt,user_prompt,model)
    else:
        print('Please enter a valid AI platform!')
        return
 
    print(response)


    extract_and_save_queries(response, entry_id)




#ENTRY_ID = 'mi5078'
#queryGeneratorAgent(ENTRY_ID)