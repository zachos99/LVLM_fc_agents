import json
import os

from models.openrouter import mm_inference_openrouter 



system_prompt = "You are a precise and objective fact-checking assistant. Your job is to assess whether a piece of external evidence supports, contradicts, or is neutral with respect to a given social media claim. You must analyze both text and referenced images (if any) and return a clear, structured JSON result. Be concise, avoid speculation, and use only the provided evidence."


def build_evidence_reasoning_user_prompt(post_analysis, evidence_text):
    return f"""
You are a fact-checking assistant.

A claim from a social media post is being evaluated against a single piece of external evidence (text with embedded images).

Your tasks:
1. Assess whether the evidence is relevant and clearly connected to the claim.
2. Determine the stance of the evidence regarding the claim: does it support, contradict, or neither (neutral)?
3. Provide a confidence score from 0.0 to 1.0 for your judgment.
4. If only partial aspects of the claim are addressed, explain what parts are supported or contradicted.
5. Extract one or more short text snippets (quotes) from the evidence that strongly influenced your decision.
6. If any images were referenced (e.g., [image 1, description="..."]), note their numeric IDs if they helped.

### CLAIM ###
{post_analysis}

### EVIDENCE TEXT ###
{evidence_text}

Now, answer in the following structured JSON format:

{{
  "valid_evidence": true or false,
  "stance": "support" | "contradict" | "neutral",
  "confidence": float between 0 and 1,
  "partial_info_note": "...",
  "key_snippets": ["...", "..."],
  "used_images": [1, 3]
}}
"""


def analyze_one_evidence(entry_id, q,search_result,model ):

    # Load post analysis
    post_path = f"models/responses/{entry_id}_response.json"
    with open(post_path, "r") as f:
        post_data = json.load(f)
    
    #print(post_data)

    # Load preprocessed evidence file
    ev_path = f"evidence_filtering/evidencePreprocessing/{entry_id}/{entry_id}_q{q}_v1_result_{search_result}.json"
    with open(ev_path, "r") as f:
        ev_data = json.load(f)
    
    #print('\n\n\n\n',ev_data)

    user_prompt = build_evidence_reasoning_user_prompt(post_data,ev_data)

    #print(prompt)

    """ """
    # Run LLM
    result = mm_inference_openrouter(system_prompt, user_prompt, model, max_tokens=10240, temperature = 0.2)

    """
        We must extract the image urls before feeding them and add them as a parameter

    """
    # 4. Save result if needed
    evidence_dir="evidence_filtering/evidenceResoning"
    os.makedirs(evidence_dir, exist_ok=True)
    out_path = f"{evidence_dir}/{entry_id}/{entry_id}_q{q}_v1_result_{search_result}_evidence_eval.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result




ENTRY_ID = 'mi2772'
MODEL = ''
analyze_one_evidence(ENTRY_ID,'1','1',MODEL)















