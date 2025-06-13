from together import Together

from dotenv import load_dotenv
import os

load_dotenv()


TOGETHER_API_KEY =  os.getenv("TOGETHER_API_KEY")


"""
Text only:
    Meta Llama 3.3 70B Instruct Turbo Free --> meta-llama/Llama-3.3-70B-Instruct-Turbo-Free
    DeepSeek R1 Distill Llama 70B Free
Vision:
    Meta Llama Vision Free (Llama-3.2-11B-Vision-Instruct) --> meta-llama/Llama-Vision-Free
"""



def mm_inference_togetherai(system_prompt,user_prompt, model, image_urls=None, max_tokens=1024, temperature=0.2):

    client = Together(api_key=TOGETHER_API_KEY)

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
        response = client.chat.completions.create(
            model=model,
            messages = messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        print("\nResponse usage:",response.usage,"\n") 
        
        return response.choices[0].message.content
    
    except Exception as e:
        print("❌ Error during vision inference:", e)
        return None




