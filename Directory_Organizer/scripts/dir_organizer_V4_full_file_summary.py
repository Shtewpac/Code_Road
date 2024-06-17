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
FINAL_SUMMARY_SYSTEM_MSG = "You are an AI assistant skilled at summarizing software projects from technical documentation and code. You will receive a combined text containing multiple files with their filenames indicated. Analyze the provided text and generate a brief summary for each file, with the summary list indicating the filename above each summary."

# Global Project Structure
PROJECT_STRUCTURE = {
    "README.md": "",
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
        "archive/": {}
    },
    "scripts/": {
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
def get_file_relocation_info(client, files_with_summaries, project_structure):
    system_msg = f"""You are an AI assistant that helps organize files within a software project's structure. 
                     You will receive a summary of the entire project, a list of files with their summaries, and the project's directory structure. 
                     Your task is to determine the most appropriate location and name for each file within the project's directory structure, considering its content and context.

                     Project Structure:
                     {json.dumps(project_structure, indent=4)}"""

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"Files with Summaries:\n{files_with_summaries}"},
    ]
    
    function_call = {
        "name": "file_relocation",
        "description": "Specify new locations and file names.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_relocations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "old_location": {"type": "string", "description": "Path to the current file location within the temporary directory"},
                            "old_file_name": {"type": "string", "description": "Current name of the file (with extension)"},
                            "new_location": {"type": "string", "description": "Path to the new directory within the project directory"},
                            "new_file_name": {"type": "string", "description": "New name for the file (with extension)"}
                        },
                        "required": ["old_location", "old_file_name", "new_location", "new_file_name"]
                    }
                }
            },
            "required": ["file_relocations"]
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
            function_args = json.loads(response_message.function_call.arguments)
            return function_args["file_relocations"]
        else:
            print("No function call detected in the response. Extracting details from content.")
            return response_message.content  # Return the raw content to be parsed
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print("Response content:", response_message.function_call.arguments)
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def relocate_and_rename_file(old_path, new_path):
    """Moves and renames a file."""
    try:
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(old_path, new_path)
        print(f"File moved from '{old_path}' to '{new_path}'")
    except Exception as e:
        print(f"Error moving file: {e}")
        
def parse_relocation_response(content):
    pattern = re.compile(
        r'\*\*File:\*\* (.+)\n\s+- \*\*Old Location:\*\* [^\n]+\n\s+- \*\*Old Name:\*\* [^\n]+\n\s+- \*\*New Location:\*\* ([^\n]+)\n\s+- \*\*New Name:\*\* ([^\n]+)'
    )
    matches = pattern.findall(content)
    file_relocations = []
    for match in matches:
        file_relocations.append({
            "old_location": ".",  # Assuming files are in the root of the temp folder
            "old_file_name": match[0],
            "new_location": match[1],
            "new_file_name": match[2]
        })
    return file_relocations


def relocate_and_rename_files(temp_path, base_path, project_structure, client):
    """Relocates and renames files based on GPT-4 suggestions."""
    files_with_summaries = summarize_directory(temp_path, ['.py', '.md'])
    print(f"Files with Summaries:\n{files_with_summaries}")

    response_content = get_file_relocation_info(client, files_with_summaries, project_structure)
    
    if isinstance(response_content, str):
        # Parse the response content to extract relocation information
        file_relocations = parse_relocation_response(response_content)
    elif isinstance(response_content, list):
        file_relocations = response_content  # Directly use the list of relocations
    else:
        file_relocations = []

    if file_relocations:
        for relocation in file_relocations:
            old_path = os.path.join(temp_path, relocation["old_file_name"])
            new_path = os.path.join(base_path, relocation["new_location"].lstrip('/'), relocation["new_file_name"])
            relocate_and_rename_file(old_path, new_path)



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

def combine_files_with_filenames(directory, extensions):
    all_content = ""
    print(f"Combining files in {directory} with filenames...")
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        file_content = f.read()
                    all_content += f"Filename: {file}\n{file_content}\n\n"
                except Exception as e:
                    print(f"Error reading {file}: {e}")

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


def summarize_directory(directory, extensions):
    print(f"\nProcessing directory: {directory}\n")
    combined_content = combine_files_with_filenames(directory, extensions)
    if combined_content:
        final_summary = summarize_text(client, combined_content, 1, FINAL_SUMMARY_SYSTEM_MSG)
        if final_summary:  # Check if final_summary is not None
            print(f"\n\nFinal Summary:\n{final_summary}\n")
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

    # # 4. Summarize the files now in the temp_folder
    # project_summary = summarize_directory(temp_folder, ['.py', '.md']) 
    # print(f"Project Summary:\n{project_summary}\n")

    # 5. Relocate and rename the files from the temp_folder to the new structure in base_path
    relocate_and_rename_files(temp_folder, base_path, PROJECT_STRUCTURE, client)  
    
    # # 6. Clean up the temp_folder
    # clean_up_temp_folder(temp_folder)
    
    print("File relocation completed.")
unknown