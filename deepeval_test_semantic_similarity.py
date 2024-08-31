# The SentenceTransformer model (which is used for semantic similarity) will be downloaded the first time this is run. This includes the model weights, 
# configuration files, and tokenizer data. This download is necessary only the first time you use the model. Once downloaded, it will be cached locally, so # subsequent runs should be faster.

from openai import OpenAI
import os
from deepeval.test_case import LLMTestCase
from sentence_transformers import SentenceTransformer, util
import warnings

# Suppress runtime warnings that might clutter the output
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Initialize the OpenAI client using the API key from environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the sentence transformer model for semantic similarity
embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Function to fetch a response from the OpenAI API
def fetch_response(prompt, context):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

# Example prompt and context to be tested
prompt = "Why did the chicken cross the road?"
context = "Cultural"

# Option to switch between dynamic and hardcoded expected responses
use_dynamic_responses = False  # Set to False to use hardcoded expected responses

if use_dynamic_responses:
    # Fetch expected responses from the API
    expected_responses = [
        fetch_response(prompt, context),
        fetch_response(prompt, context),
        fetch_response(prompt, context)
    ]
else:
    # Use hardcoded expected responses
    expected_responses = [
        "To get to the other side.",
        ("Because its dopaminergic neurons fired synchronously across the synapses of its caudate nucleus, "
         "triggering motor contractions propelling the organism forward, to a goal predetermined by its hippocampal road mappings.")
    ]

# Fetch the actual output from the model using the same API call
model_completion = fetch_response(prompt, context)

# Define a custom similarity function 
def semantic_similarity(actual_output, expected_outputs, threshold=0.3):
    actual_embedding = embedding_model.encode(actual_output, convert_to_tensor=True)
    expected_embeddings = embedding_model.encode(expected_outputs, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(actual_embedding, expected_embeddings)
    return any(score >= threshold for score in cosine_scores[0])

# Evaluate the test case directly using the custom similarity function
passed = semantic_similarity(model_completion, expected_responses)

# Report the result
print("Test Report:")
print(f"Input: {prompt}")
print(f"Expected Output: {expected_responses}")
print(f"Actual Output: {model_completion}")
print(f"Result: {'Pass' if passed else 'Fail'}")


