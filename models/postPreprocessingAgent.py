
from datetime import datetime

from models.togetherai import mm_inference_togetherai 
from models.openrouter import mm_inference_openrouter
from models.utils import get_entry_info, upload_to_imgbb, save_response_to_json, format_timestamp


def build_system_prompt():
    today_date = datetime.today().strftime('%B %d, %Y') 
    return f"You are a fact-checking assistant. Today's date is {today_date}. Your job is to analyze a social media post (text + image) and extract important information to help verify whether it is true, misleading, or manipulated."


def build_user_prompt(tweet_timestamp,tweet_text):
    return f"""
    Here is a social media post created at {tweet_timestamp}: 
    Text: {tweet_text}. \nImage is given below.
    Based on the image and post text:

    1. **Image Description**: Describe what is visually shown in the image (scene, objects, people, setting).
    2. **OCR**: Look carefully for any text inside the image, including signs, labels, headlines, or screenshots. Transcribe all readable text as accurately as possible. If there is no text, write 'No visible text'.
    3. **Manipulation Signs**:Look closely for any signs that the image may have been AI-generated, manipulated, or edited. Signs may include:
        -Distorted or unnatural hands, faces, or shadows
        -Inconsistent lighting or reflections
        -Blurry or melted objects
    If such artifacts are present, describe them. If the image looks realistic and free of obvious manipulation, say “No obvious signs of manipulation.
    4. **Named Entities**: List all named entities (people, organizations, places, dates) mentioned in the text or visually depicted in the image
    5. **5Ws Extraction**:
    - Who is involved?
    - What is happening?
    - Where is this taking place?
    - When is it happening (explicit or implied)?
    - Why is this happening (if stated)?
    6. **Image-Text Alignment**: Does the image visually match the claim made in the post text?
    7. **Emotive Language or Logical Fallacies**: Check the post text for emotionally charged language, exaggerations, or logical fallacies (e.g. appeal to fear, false cause, hate speech).
    8. **Timestamp Consistency Check**: 
    - First, check if the post text or image explicitly references a time in the past
    - If it does, and the image appears consistent with that historical reference, do not consider it inconsistent.
    - Only flag a temporal inconsistency if the post implies a recent or real-time event but the image or information clearly comes from a different time

    If any information is unclear or not visible, say “Unclear”.
    Respond in bullet point format for each section.
    """





def postPreprocessingAgent(entryID,platform,model):

    entry = get_entry_info(entryID)
    #print("Tweet Text:", entry["tweetText"])
    #print("\nNote Text:", entry["noteText"])
    #print("\nMedia Files:", entry["tweetMediaFiles"])


    tweet_text = entry["tweetText"]
    image_path = entry['tweetMediaFiles'][0]

    tweet_timestamp = format_timestamp(entry['tweetCreatedAt'])

    image_url = upload_to_imgbb(image_path)
    print(f"\nImage generated URL is: {image_url}\n")

    
    system_prompt = build_system_prompt()

    user_prompt = build_user_prompt(tweet_timestamp,tweet_text)


    print(f"\nAsking {model}...\n")


    if(platform=='openrouter'):
        print("\nUsing OpenRouter API...\n")
        response = mm_inference_openrouter(system_prompt,user_prompt,model, image_url)
    elif(platform=='togetherai'):
        print("\nUsing TogetherAI API...\n")
        response = mm_inference_togetherai(system_prompt,user_prompt,model, image_url)
    else:
        print('Please enter a valid AI platform!')
        return
    
    print("\nResponse:\n", response)

    save_response_to_json(tweet_text,image_path,response,entryID)







#ENTRY_ID = 'mi5078'
#postPreprocessingAgent(ENTRY_ID)


