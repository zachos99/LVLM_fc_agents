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

POST_PROCESSING_PLATFORM = 'openrouter'
POST_PROCESSING_MODEL = 'qwen/qwen-2.5-vl-7b-instruct:free' # 'qwen/qwen2.5-vl-32b-instruct:free' #

QUERY_GENERATOR_PLATFORM = 'togetherai'
QUERY_GENERATOR_MODEL = 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free'

NUM_QUERIES = 2 # How many queries to generate for normal search
RESULTS_PER_QUERY = 3

"""
    Optionally, we can set and experiment with the max_tokens and temperature varibles
    Simply pass max_tokens=MAX_TOKENS,temperature=TEMPERATURE in queryGeneratorAgent()
    Default values are 1024 and 0.2
        🔸 max_tokens is the maximum length of the output
                higher values (1024-4096) for longer outputs like articles or analyses
                limited for short tasks like classification or query generation
        🔸 temperature controls randomness / creativity of the output
                0       --> deterministic (always gives the same answer)
                0.2-0.4 --> precise and focused (good for fact-checking, extraction)
                0.7-1.0 --> more creative, diverse (idea generation, writing)
                For fact-checking / structured queries --> use 0.2-0.4.
"""

MAX_TOKENS = 512
TEMPERATURE = 0.2



ENTRY_ID = 'ma2975'



print('\nAnalyzing entry:', ENTRY_ID)

#postPreprocessingAgent(ENTRY_ID, POST_PROCESSING_PLATFORM, POST_PROCESSING_MODEL)

print(f"\n\nGenerating {NUM_QUERIES} queries...\n")

#queryGeneratorAgent(ENTRY_ID, QUERY_GENERATOR_PLATFORM, QUERY_GENERATOR_MODEL, NUM_QUERIES, max_tokens=MAX_TOKENS,temperature=TEMPERATURE)


print("\n\nSearching the web...") # Also saving search results somewhere?

run_searches_from_query_file(entry_id=ENTRY_ID, num_results = RESULTS_PER_QUERY)



