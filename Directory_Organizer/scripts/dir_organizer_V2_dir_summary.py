import os
import shutil
import openai
from openai import OpenAI
import json
import time
import re


API_KEY = "<YOUR_API_KEY>"

CHUNK_SIZE = 64000  # Adjust chunk size as needed
CHUNK_SUMMARY_SYSTEM_MSG = "You are an AI assistant skilled at summarizing software projects from technical documentation and code. Analyze the provided text (which may be a fragment of a larger project) and generate a brief summary."
FINAL_SUMMARY_SYSTEM_MSG = "You are an AI assistant skilled at summarizing software projects from technical documentation and code. Analyze the provided text (which may be a fragment of a larger project) and generate a brief summary."

# Global Project Structure
PROJECT_STRUCTURE = {
    "README.md": "",
    "LICENSE": "",
    "setup.py": "",
    "requirements.txt": "",
    "docs/": {},
    "src/": {
        "__init__.py": "",
        "config.py": "",
        "utils.py": "",
        "main.py": ""
    },
    "data/": {
        "raw/": {},
        "processed/": {}
    },
    "notebooks/": {
        "01-first-logical-notebook.ipynb": "",
        "02-second-logical-notebook.ipynb": "",
        "archive/": {}
    },
    "scripts/": {
        "script1.py": "",
        "script2.py": ""
    },
    "tests/": {
        "test_config.py": "",
        "test_custom_funcs.py": ""
    },
    "environment.yml": ""
}

def create_file(file_path, content=''):
    """Creates a file with the given content at the specified path."""
    with open(file_path, 'w', encoding='utf-8') as f:  # Explicit encoding to avoid potential issues
        f.write(content)



def move_existing_files_to_temp(base_path, temp_folder):
    """Moves existing files to a temporary folder, handling conflicts and skipping the temp folder itself."""
    os.makedirs(temp_folder, exist_ok=True)
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if item == os.path.basename(temp_folder):  # Skip the temp folder itself
            continue

        temp_item_path = os.path.join(temp_folder, item)
        if os.path.exists(temp_item_path):
            # Handle conflicts by appending a number to the filename
            i = 1
            while os.path.exists(f"{temp_item_path}_{i}"):
                i += 1
            temp_item_path = f"{temp_item_path}_{i}"
        shutil.move(item_path, temp_item_path)  # Use the adjusted path
    print(f"Existing files moved to temporary folder: {temp_folder}")


def create_project_structure(base_path, structure=PROJECT_STRUCTURE):
    def create_structure(path, structure):
        for name, content in structure.items():
            full_path = os.path.join(path, name)
            if isinstance(content, dict):
                os.makedirs(full_path, exist_ok=True)
                create_structure(full_path, content)
            else:
                create_file(full_path, content)

    create_structure(base_path, structure)
    print(f"Project structure created at: {base_path}")

# Function for GPT-4 File Relocation
def get_file_relocation_info(client, project_summary, file_summary, project_structure):
    system_msg = f"""You are an AI assistant that helps organize files within a software project's structure. 
                     You will receive a summary of the entire project, a summary of a specific file, and the project's directory structure. 
                     Your task is to determine the most appropriate location and name for this file within the project's directory structure, considering its content and context.

                     Project Structure:
                     {json.dumps(project_structure, indent=4)}"""

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"Project Summary:\n{project_summary}\n\nFile Summary:\n{file_summary}"},
    ]
    
    function_call = {
        "name": "file_relocation",
        "description": "Specify new location and file name.",
        "parameters": {
            "type": "object",
            "properties": {
                "new_location": {"type": "string", "description": "Path to the new directory within the project directory"},
                "new_file_name": {"type": "string", "description": "New name for the file (with extension)"}
            },
            "required": ["new_location", "new_file_name"]
        }
    }
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            functions=[function_call],
            function_call="auto"
        )
        
        # Print the entire response for debugging
        # print("API Response:", response)
        
        response_message = response.choices[0].message
        if response_message.function_call:
            print("\n\nFunction Call: ", response_message.function_call)
            function_args = json.loads(response_message.function_call.arguments)
            new_location = function_args["new_location"]
            new_file_name = function_args["new_file_name"]
            return new_location, new_file_name
        else:
            print("No function call detected in the response. Extracting details from content.")
            content = response_message.content
            print("Content:", content)

            # Use regex to find the new location and file name
            location_match = re.search(r'"new_location":\s*"([^"]+)"', content)
            name_match = re.search(r'"new_file_name":\s*"([^"]+)"', content)

            if location_match and name_match:
                new_location = location_match.group(1)
                new_file_name = name_match.group(1)
                return new_location, new_file_name
            else:
                print("Could not extract new location and file name from content.")
                return None, None
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print("Response content:", response_message.function_call.arguments)
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None


def relocate_and_rename_file(file_path, new_location, new_file_name, base_path):
    """Moves and renames a file, handling conflicts by appending a number to the file name."""
    new_location_path = os.path.join(base_path, new_location)
    new_file_path = os.path.join(new_location_path, new_file_name)
    base_name, ext = os.path.splitext(new_file_name)
    
    # Ensure the new location directory exists
    os.makedirs(new_location_path, exist_ok=True)
    
    # Handle file name conflicts
    i = 1
    while os.path.exists(new_file_path):
        new_file_path = os.path.join(new_location_path, f"{base_name}_{i}{ext}")
        i += 1

    # Move the file
    shutil.move(file_path, new_file_path)
    print(f"File '{file_path}' moved to '{new_file_path}'")


def relocate_and_rename_files(temp_path, base_path, project_summary, project_structure, client):
    """Relocates and renames files based on GPT-4 suggestions."""
    for root, _, files in os.walk(temp_path):
        for file_name in files:
            print("Relocating and renaming file: ", file_name)
            file_path = os.path.join(root, file_name)
            with open(file_path, "r") as f:
                file_content = f.read()
            new_location, new_file_name = get_file_relocation_info(client, project_summary, file_content, project_structure) 
            print(f"New Location: {new_location}, New File Name: {new_file_name}")
            if new_location and new_file_name:
                relocate_and_rename_file(file_path, new_location, new_file_name, base_path)


def clean_up_temp_folder(temp_folder):
    """Safely deletes the temporary folder."""
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    
# File Handling Functions
def combine_files(directory, extensions):
    all_content = ""
    combined_files = []  # List to store the names of combined files
    print(f"Combining files in {directory}...")
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                combined_files.append(os.path.join(root, file))  # Add file to the list
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='replace') as f:
                        all_content += f.read() + "\n\n"
                except Exception as e:
                    print(f"Error reading {file}: {e}")

    print("Combined the following files:")
    for file in combined_files:
        print(f"- {file}")

    return all_content

def split_into_chunks(text, chunk_size):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# OpenAI Interaction
def summarize_text(client, text_chunk, chunk_index, system_message, max_retries=5, retry_delay=10): 
    """Summarizes text with GPT-4, including retry logic for rate limits."""
    retries = 0
    while retries < max_retries:
        print(f"Summarizing chunk {chunk_index}... (Attempt {retries + 1})")  # Retry tracking
        # print(f"Chunk content: {text_chunk[:100]}...")  # Display a snippet of the chunk content
        # print(f"Chunk content: {text_chunk}")  # Display a snippet of the chunk content
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": text_chunk}
                ]
            )
            return response.choices[0].message.content
        except openai.RateLimitError as e: 
            print("Rate limit exceeded. Pausing and retrying...")
            time.sleep(retry_delay)
            retries += 1
        except openai.OpenAIError as e:
            print(f"OpenAI Error: {e}")
            return None
    print(f"Failed to summarize chunk {chunk_index} after {max_retries} attempts.")
    return None  # Return None to indicate failure

# Directory Summarization Function
def summarize_directory(directory, extensions):
    print(f"\nProcessing directory: {directory}\n")
    combined_content = combine_files(directory, extensions)
    if combined_content:
        text_chunks = split_into_chunks(combined_content, CHUNK_SIZE)
        print(f"Split into {len(text_chunks)} chunks.")
        # print(f"Chunk content: {text_chunks[0][:100]}...")  # Display a snippet of the first chunk content

        if len(text_chunks) == 1:
            # Handle the case where there's only one chunk
            final_summary = summarize_text(client, text_chunks[0], 1, FINAL_SUMMARY_SYSTEM_MSG) 
        else:
            # Multiple chunks - proceed with the original logic
            summaries = []
            for i, chunk in enumerate(text_chunks):
                summary = summarize_text(client, chunk, i + 1, CHUNK_SUMMARY_SYSTEM_MSG)
                if summary:
                    summaries.append(summary)

            final_summary = summarize_text(client, "\n\n".join(summaries), 1, FINAL_SUMMARY_SYSTEM_MSG)  

        if final_summary: # Check if final_summary is not None
            return final_summary
    else:
        print(f"No relevant files found in {directory}.")

if __name__ == "__main__":
    client = OpenAI(api_key=API_KEY)

    base_path = "Directory_Organizer/Test_Dir/Coding_Project_Summarizer"
    temp_folder = os.path.join(base_path, "temp_folder")
    
    # 1. Clean up any existing temp_folder to start fresh
    clean_up_temp_folder(temp_folder)

    # 2. Move existing files to the temp_folder
    move_existing_files_to_temp(base_path, temp_folder)

    # 3. Create the new project structure in the original base_path
    create_project_structure(base_path)

    # 4. Summarize the files now in the temp_folder
    project_summary = summarize_directory(temp_folder, ['.py', '.md']) 
    print(f"Project Summary:\n{project_summary}\n")

    # 5. Relocate and rename the files from the temp_folder to the new structure in base_path
    relocate_and_rename_files(temp_folder, base_path, project_summary, PROJECT_STRUCTURE, client)  
    
    # 6. Clean up the temp_folder
    clean_up_temp_folder(temp_folder)
    
    print("File relocation completed.")
unknown