import tiktoken
import openai

from messages import *

OPENAI_API_KEY = "<YOUR_OPENAI_API_KEY>"

openai.api_key = OPENAI_API_KEY

MAX_TOKENS = {
    "gpt-3.5-turbo-0613": 4096,
    "gpt-3.5-turbo-16k-0613": 16384,
    "gpt-4": 8192,
    "gpt-4-0314": 8192,
    "gpt-4-32k-0314": 32768,
    "gpt-4-0613": 8192,
    "gpt-4-32k-0613": 32768,
}
 
C = 300

# SYSTEM_MESSAGE = "You are an assistant that condenses text into a summary while maintaining the essential information."
# SYSTEM_MESSAGE = "You are an assistant that helps summarize the concepts covered in each lecture section of a text"
SYSTEM_MESSAGE = "You are an assistant that summarizes parts of a chapter in a book, in your summary, include page numbers and chapter titles/sections"

# CONCAT_SYSTEM_MESSAGE = "You are an assistant that receives summarized chunks of a long original message and combines them to make a full comprehensive summary."
CONCAT_SYSTEM_MESSAGE =  "Reorganize this"

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

# Calculate the remaining tokens that can be used for the message
def calculate_remaining_tokens(model, system_msg, max_response_tokens):
    
    remaining_tokens = max_tokens_for_model - tokens_for_system_msg - max_response_tokens - C
    print("Max Response Tokens:", max_response_tokens)
    print("Remaining Tokens:", remaining_tokens)

    return remaining_tokens

# Break the input message into chunks that fit within the model's token limit
def create_message_chunks(words, remaining_tokens, model):
    chunks = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        word_tokens = num_tokens_from_string(word, tiktoken.encoding_for_model(model).name)
        
        # If adding the next word exceeds the token limit, save the current chunk and start a new one
        if current_tokens + word_tokens > remaining_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_tokens = word_tokens
        else:
            current_chunk.append(word)
            current_tokens += word_tokens

    # Add any remaining chunk to the list
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# Get the summaries for each chunk using OpenAI API with a limit on summary length
def get_summaries(chunks, model, system_msg, summary_tokens):
    summaries = []
        
    for chunk in chunks:
        full_msg = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": chunk}
        ]
        openai_response = openai.ChatCompletion.create(
            model=model,
            messages=full_msg,
            max_tokens=summary_tokens  # Set the summary length based on summary_length
        )
        summaries.append(openai_response['choices'][0]['message']['content'])
    
    return summaries

def get_max_tokens(model):
    return MAX_TOKENS.get(model, 4096)

# Main function to condense a given text using a specific model
def condense_text(msg, summary_model="gpt-3.5-turbo-16k-0613", summary_length="short", combine_model="gpt-3.5-turbo-16k-0613", system_msg=SYSTEM_MESSAGE, concat_system_msg=CONCAT_SYSTEM_MESSAGE):
    print("Original Message:", msg)
    max_tokens_for_summary_model = MAX_TOKENS.get(summary_model, 4096)
    max_summary_tokens = None
    # Check if summary_length can be converted to an integer
    try:
        max_summary_tokens = int(summary_length)
    except ValueError:
        # If not, proceed with string-based conditions
        if summary_length == "short":
            max_summary_tokens = 50  # Limit to 50 tokens for short summaries
        elif summary_length == "medium":
            max_summary_tokens = 200  # Limit to 200 tokens for medium summaries
        elif summary_length == "long":
            max_summary_tokens = 400  # Limit to 400 tokens for long summaries
        else:
            raise ValueError("Invalid summary length. Choose from 'short', 'medium', 'long', or a number of tokens.")
    
    print("Max Summary Tokens 1:", max_summary_tokens)
    max_tokens_for_model = get_max_tokens(summary_model)
    print("Max Tokens for Model:", max_tokens_for_model)
    tokens_for_system_msg = num_tokens_from_string(system_msg, tiktoken.encoding_for_model(summary_model).name)
    # If the max_response_tokens is too large, reduce it be the the maximum allowed that's less than half of the model's token limit - the system message tokens - C
    if max_summary_tokens >= max_tokens_for_model/2:
        max_summary_tokens = int(max_tokens_for_model/2 - tokens_for_system_msg - C)
    
    print("Max Summary Tokens 2:", max_summary_tokens)
    # Calculate the remaining tokens that can be used for the message
    # remaining_tokens = calculate_remaining_tokens(summary_model, system_msg, max_summary_tokens)
    remaining_tokens = int(max_tokens_for_model - tokens_for_system_msg - max_summary_tokens - C)

    print(f"Remaining Tokens: {remaining_tokens}")

    # Split the original message into words and create chunks
    words = msg.split(" ")
    chunks = create_message_chunks(words, remaining_tokens, summary_model)

    # print("\n\nChunks:", chunks)
    # print("\nFinal Chunk:", chunks[-1])
    print("\n\nNumber of chunks:", len(chunks))

    # Get summaries for each chunk
    summaries = get_summaries(chunks, summary_model, system_msg, max_summary_tokens)
    
    # Combine all summaries into one message
    concat_msg = "Here are the summarized chunks of the original message:\n" + "\n".join([f"\nSummary #{i+1}: {summary}" for i, summary in enumerate(summaries)])

    # Finalize the message for generating a comprehensive summary
    full_concat_msg = [
        {"role": "system", "content": concat_system_msg},
        {"role": "user", "content": concat_msg}
    ]
    print("Concat Message:", concat_msg)
    # Max tokens for the combine model is the max tokens for the model minus the system message tokens
    max_combine_tokens = get_max_tokens(combine_model) - num_tokens_from_string(concat_system_msg, tiktoken.encoding_for_model(combine_model).name)
    print("Max Combine Tokens:", max_combine_tokens)
    # Generate the comprehensive summary using OpenAI API    
    openai_response = openai.ChatCompletion.create(
        model=combine_model,
        messages=full_concat_msg,
        max_tokens=max_combine_tokens
    )
    
    final_summary = openai_response['choices'][0]['message']['content']
    # print("Final Summary:", final_summary)
    
    return final_summary


# Testing the function
msg = ch1

# condensed_msg = condense_text(msg, summary_model= "gpt-3.5-turbo-16k-0613", summary_length="4000", combine_model="gpt-4")
# condensed_msg = condense_text(msg, summary_model= "gpt-3.5-turbo-0613", summary_length="2000", combine_model="gpt-4")
condensed_msg = condense_text(msg, summary_model= "gpt-3.5-turbo-16k-0613", summary_length="3000", combine_model="gpt-4")
# condensed_msg = condense_text(msg, summary_model= "gpt-4", summary_length="long", combine_model="gpt-4")

print("\n\nCondensed Message:", condensed_msg)