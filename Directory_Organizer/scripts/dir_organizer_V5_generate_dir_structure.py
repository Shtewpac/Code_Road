import os
import shutil
import openai
from openai import OpenAI
import json
import time
import re

TEST_SUMMARY = """### Filename: Dir_Summarizer_V1.py

This script combines and summarizes Python and Markdown files in a specified directory using OpenAI's GPT-4 model. By reading files with specified extensions, it aggregates their contents, splits them into manageable chunks, and generates summaries using the OpenAI API. The final summary is saved to a Markdown file.   

**Key Features:**
- Combines files from a directory.
- Splits content into chunks for efficient API processing.
- Summarizes each chunk using OpenAI.
- Handles rate limits and retries.
- Saves the summarized output to a Markdown file.

### Filename: Dir_Summarizer_V2.py

This updated script improves upon the first version by systematizing file paths and naming conventions and providing better print statements for debugging. It processes multiple directories within a root directory and appends the summaries to a single Markdown file. Notable improvements include clearing existing summary files and skipping virtual environment directories.

**Key Features:**
- Processes multiple directories.
- Appends summaries to a single, customizable Markdown file.
- Skips common virtual environment directories.
- Improved file handling and log messages.

### Filename: Dir_Summarizer_V3.py

The third iteration of the summarizer script introduces a retry mechanism for handling API rate limits and errors. It differentiates between multiple and single chunk summaries and adds detailed print statements for better debugging. The script still processes multiple directories and appends summaries to a single Markdown file.

**Key Features:**
- Retry mechanism for API rate limits.
- Distinguishes between single and multiple chunks.
- Improved error handling and print statements.
- Maintains structure for processing multiple directories.

### Filename: Dir_Summarizer_V4_Version_Analysis.py

This version focuses on evaluating different approaches and consolidating improvements from previous scripts. It employs the same retry mechanism and separation of single and multiple chunk summaries, ensuring robust error handling. The script processes multiple directories, clearing existing summary files and appending new summaries to a specified Markdown file.

**Key Features:**
- Analyzes and consolidates different summation approaches.
- Maintains robust retry and error handling mechanisms.
- Processes multiple directories and clears existing summaries.
- Saves outputs to a consistent Markdown file structure.

These scripts serve as iterative improvements for summarizing documentation and code across multiple directories using OpenAI’s GPT models. Each version enhances functionality, error handling, and overall robustness."""

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



def get_new_directory_structure(client, files_with_summaries):
    system_msg = """You are an AI assistant that helps generate a directory structure for a software project.
                    You will receive a summary of the entire project, with descriptions of each file.
                    Your task is to generate an appropriate directory structure for the project, considering its content and context.
                    Ensure to include directories for scripts, tests, output, configuration, and documentation (like README.md and other docs).
                    The structure should be returned as a JSON object with appropriate folder and file names."""

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"Files with Summaries:\n{files_with_summaries}"},
    ]

    function_call = {
        "name": "generate_directory_structure",
        "description": "Generate a directory structure for the project.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_structure": {
                    "type": "object",
                    "description": "The directory structure for the project",
                    "properties": {
                        "directories": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Name of the directory"},
                                    "files": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string", "description": "Name of the file"},
                                                "description": {"type": "string", "description": "Description of the file"},
                                                "content": {"type": "string", "description": "Content of the file"}
                                            },
                                            "required": ["name", "description"]
                                        }
                                    }
                                },
                                "required": ["name"]
                            }
                        }
                    },
                    "required": ["directories"]
                }
            },
            "required": ["project_structure"]
        }
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            functions=[function_call],
            function_call="auto"
        )

        response_message = response.choices[0].message
        if response_message.function_call:
            function_args = json.loads(response_message.function_call.arguments)
            return function_args["project_structure"]
        else:
            print("No function call detected in the response. Extracting details from content.")
            return None
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print("Response content:", response_message.function_call.arguments)
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def create_project_structure_from_generated(base_path, temp_folder, structure):
    def create_structure(path, structure):
        for directory in structure.get("directories", []):
            dir_path = os.path.join(path, directory["name"])
            os.makedirs(dir_path, exist_ok=True)
            for file in directory.get("files", []):
                print("File name:", file["name"])
                file_path = os.path.join(dir_path, file["name"])
                temp_file_path = os.path.join(temp_folder, file["name"])  # Assuming files in temp_folder are directly in the root

                new_content = file.get("content", "unknown")

                if os.path.exists(temp_file_path):
                    with open(temp_file_path, 'r', encoding='utf-8') as existing_file:
                        existing_content = existing_file.read()
                    new_content = existing_content + "\n" + new_content

                create_file(file_path, new_content)  # Create file with the combined content

    create_structure(base_path, structure)
    print(f"Project structure created at: {base_path}")
    
def get_unknown_files(base_path):
    unknown_files = []
    for root, _, files in os.walk(base_path):
        print("Files:", files)
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content == "unknown":
                    unknown_files.append(file_path)
    return unknown_files

                    
    
def create_project_structure_from_generated_2(base_path, structure):
    def create_structure(path, structure):
        for directory in structure.get("directories", []):
            dir_path = os.path.join(path, directory["name"])
            os.makedirs(dir_path, exist_ok=True)
            for file in directory.get("files", []):
                print("File name:", file["name"])
                file_path = os.path.join(dir_path, file["name"])
                # if the content is not "unknown", use the provided content
                content = file.get("content", "unknown")
                create_file(file_path, content)

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

def combine_all_files(base_folder):
    combined_content = ""
    for root, _, files in os.walk(base_folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    combined_content += f"\n\n---\nFile: {file}\nPath: {file_path}\n---\n{file_content}\n"
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    return combined_content

def get_new_content_for_unknown_files(client, combined_content, unknown_files):
    system_msg = """You are an AI assistant that generates content for files with unknown content based on the provided project context.
                    You will receive a combined content of all project files and a list of files with unknown content.
                    Generate appropriate content for these files."""

    unknown_files_info = "\n".join(unknown_files)

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"Combined Content:\n{combined_content}\n\nUnknown Files:\n{unknown_files_info}"}
    ]

    function_call = {
        "name": "generate_file_contents",
        "description": "Generate content for files with unknown content.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_contents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "file_name": {"type": "string", "description": "Name of the file"},
                            "content": {"type": "string", "description": "Content of the file"}
                        },
                        "required": ["file_name", "content"]
                    }
                }
            },
            "required": ["file_contents"]
        }
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            functions=[function_call],
            function_call="auto"
        )

        response_message = response.choices[0].message
        if response_message.function_call:
            function_args = json.loads(response_message.function_call.arguments)
            return {item["file_name"]: item["content"] for item in function_args["file_contents"]}
        else:
            print("No function call detected in the response. Extracting details from content.")
            return {}
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print("Response content:", response_message.function_call.arguments)
        return {}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {}



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
    
    combined_content = combine_all_files(temp_folder)
    print(f"Combined Content:\n{combined_content}\n")
    
    # 3. Summarize the files now in the temp_folder
    project_summary = TEST_SUMMARY 
    print(f"Project Summary:\n{project_summary}\n")

    # 4. Generate the new directory structure
    new_project_structure = get_new_directory_structure(client, project_summary)
    if new_project_structure:
        print(f"Generated Project Structure:\n{json.dumps(new_project_structure, indent=4)}\n")
    else:
        print("Failed to generate project structure. Using predefined structure.")
        new_project_structure = PROJECT_STRUCTURE  # Fallback to predefined structure if generation fails
        
    print(f"New Project Structure:\n{json.dumps(new_project_structure, indent=4)}\n")
    
    create_project_structure_from_generated(base_path, temp_folder, new_project_structure)
    
    # 6. Identify files with "unknown" content
    unknown_files = get_unknown_files(base_path)
    print("Unknown Files:", unknown_files)
    
    # 7. Generate content for files with "unknown" content using function call
    if unknown_files:
        generated_contents = get_new_content_for_unknown_files(client, combined_content, unknown_files)
        print("Generated Contents for Unknown Files:", generated_contents)
        for file_path in unknown_files:
            file_name = os.path.basename(file_path)
            if file_path in generated_contents:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(generated_contents[file_path])

    # 8. Create the new project structure in the original base_path
    create_project_structure_from_generated_2(base_path, new_project_structure)

    # # 9. Clean up the temp_folder
    # clean_up_temp_folder(temp_folder)
    
    print("File relocation completed.")

unknown