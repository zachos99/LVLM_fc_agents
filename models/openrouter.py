from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


"""
---------------------------------------------
    Multimodal free models in Open Router:
---------------------------------------------
    meta-llama/llama-3.2-11b-vision-instruct:free
    qwen/qwen2.5-vl-{72,32,3}b-instruct:free
    qwen/qwen-2.5-vl-7b-instruct:free
    opengvlab/internvl3-1{4,2}b:free

---------------------------------------------
    Text-only free models in Open Router:
---------------------------------------------
    google/gemma-3n-e4b-it:free
    qwen/qwen-2.5-72b-instruct:free
    google/gemini-2.0-flash-exp:free

"""





def mm_inference_openrouter(system_prompt, user_prompt, model, image_url=None, max_tokens=1024, temperature = 0.2):
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

    if image_url: 
        user_content.append({ "type": "image_url", "image_url": {"url": image_url} })

    messages.append({
        "role": "user",
        "content": user_content
    })

    try:
        completion = client.chat.completions.create(
            model=model, 
            messages=messages,
            max_tokens=max_tokens,
            temperature = temperature
        )

        # Defensive check before accessing choices
        if completion and completion.choices and len(completion.choices) > 0:
            return completion.choices[0].message.content
        else:
            print("⚠️ No choices returned. Full response:")
            print(completion)
            return None

    except Exception as e:
        print("❌ API call failed:", e)
        return None
    


