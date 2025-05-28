""" """
from transformers import AutoProcessor, AutoModelForImageTextToText
import torch
import pandas as pd
from PIL import Image

model_path = "HuggingFaceTB/SmolVLM2-500M-Instruct" # SmolVLM2-500M-Instruct  SmolVLM2-256M-Video-Instruct 
# SmolVLM2-2.2B-Instruct --> Out of mem
processor = AutoProcessor.from_pretrained(model_path)
model = AutoModelForImageTextToText.from_pretrained(
    model_path,
    torch_dtype=torch.bfloat16,
    _attn_implementation="flash_attention_2",
    device_map={"": "cuda"} ,  # or device_map="auto"   device_map={"": "cuda"}
)
torch.cuda.empty_cache()
model.to("cuda")


###########################################################################
######################## Multiple Images Inference #########################
###########################################################################
""" """
df = pd.read_csv("../image_keyword_notes/manipulated_combined.csv")  
tweet_id = 876

print(df.loc[df['id'] == tweet_id, 'tweetMediaFiles'].values[0] )
tweet_image_path = f"../image_keyword_notes/twikit/{ df.loc[df['id'] == tweet_id, 'tweetMediaFiles'].values[0] }"

tweet_text = df.loc[df['id'] == tweet_id, 'tweetText'].values[0]
#print(tweet_text)
tweet_note = df.loc[df['id'] == tweet_id, 'noteSummary'].values[0]



# Prepare the image
image = Image.open(tweet_image_path).convert("RGB")


messages = [
    {
    "role": "user",
    "content": [
        # IN THAT ORDER OTHERWISE IT DESCRIBES THE PICTURE
        {"type": "image"}, # Just the placeholder, actual image is added below
        {"type":  "text", "text": 
         (
            f""" You are an expert AI fact-checking assistant. Your task is to classify a social media post using:
            a) The **post's text** and its **attached image**
            b) A **Community Note**, which is a human-written explanation about the truthfulness of the post.
            Use the Community Note as a strong signal for your classification, along with the image and text. Ignore any URLs. Classification labels are:
            'miscaptioned' if the image is real, but used out-of-context or misleadingly.
            'manipulated' if the image is digitally altered or fake.
            'factually correct' if the post is truthful and accurate.
            Post Text is: "{tweet_text}"
            Community Note is: "{tweet_note}"
            Think step by step: First analyze the post (text and image), then use the Community Note to verify truthfulness. Then give your classification.\n\n"""
         )}, #**Instruction**: Return only the classification label ('miscaptioned', 'manipulated', or 'factually correct'), followed by a short 1-2 sentence explanation.\n\n"""
         
    ]
}
]


prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
inputs = processor(text=prompt, images=[image], return_tensors="pt")
inputs = inputs.to(model.device, dtype=torch.bfloat16)

print("Input token sequence length:", inputs["input_ids"].shape[1])


generated_ids = model.generate(**inputs, do_sample=True, max_new_tokens=512)
generated_texts = processor.batch_decode(generated_ids, skip_special_tokens=True)


print('\n',generated_texts[0])





