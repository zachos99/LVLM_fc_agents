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



def mm_inference_togetherai(system_prompt,user_prompt, model, image_url=None):

    client = Together(api_key=TOGETHER_API_KEY)

    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    user_content = [{"type": "text", "text": user_prompt}]

    if image_url: 
        user_content.append({ "type": "image_url", "image_url": {"url": image_url} })

    messages.append({
        "role": "user",
        "content": user_content
    })
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages = messages,
            max_tokens=1024,
            temperature=0.2
        )

        print("\nResponse usage:",response.usage) 
        
        return response.choices[0].message.content
    
    except Exception as e:
        print("❌ Error during vision inference:", e)
        return None




