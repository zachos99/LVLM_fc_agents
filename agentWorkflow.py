from models.postPreprocessingAgent import postPreprocessingAgent
from models.queryGeneratorAgent import queryGeneratorAgent


from web_search.google_search import run_searches_from_query_file



"""
    Workflow of AI Agents
"""

"""
    Platforms: 
        Use one of:
            'openrouter'
            'togetherai'
 -----------------------------------------------------------------------------------------------------
    Models:
        OpenRouter:
            Multimodal:
                meta-llama/llama-3.2-11b-vision-instruct:free
                qwen/qwen2.5-vl-{72,32,3}b-instruct:free
                qwen/qwen-2.5-vl-7b-instruct:free
                opengvlab/internvl3-1{4,2}b:free
            Text-only:
                google/gemma-3n-e4b-it:free
                qwen/qwen-2.5-72b-instruct:free
        Together AI:
            Multimodal:
                meta-llama/Llama-Vision-Free --> Llama-3.2-11B-Vision-Instruct
            Text-only:
                meta-llama/Llama-3.3-70B-Instruct-Turbo-Free    --> Meta Llama 3.3 70B Instruct Turbo Free  
                deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free  --> DeepSeek R1 Distill Llama 70B Free
 -----------------------------------------------------------------------------------------------------
"""


ENTRY_ID = 'fa0097'

POST_PROCESSING_PLATFORM = 'openrouter'
POST_PROCESSING_MODEL = 'qwen/qwen-2.5-vl-7b-instruct:free'

QUERY_GENERATOR_PLATFORM = 'togetherai'
QUERY_GENERATOR_MODEL = 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free'

NUM_QUERIES = 2 # How many queries to generate
RESULTS_PER_QUERY = 2


""" """

print('\nAnalyzing entry:', ENTRY_ID)

postPreprocessingAgent(ENTRY_ID, POST_PROCESSING_PLATFORM, POST_PROCESSING_MODEL)

print(f"\n\nGenerating {NUM_QUERIES} queries...\n")

queryGeneratorAgent(ENTRY_ID, QUERY_GENERATOR_PLATFORM, QUERY_GENERATOR_MODEL, NUM_QUERIES)


print("\n\nSearching the web...")
# Also saving search results somewhere?

run_searches_from_query_file(entry_id=ENTRY_ID,is_image_search=False, num_results = RESULTS_PER_QUERY)



