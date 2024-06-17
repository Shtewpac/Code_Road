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



# def move_existing_files_to_temp(base_path, temp_folder):
#     """Moves existing files to a temporary folder, handling conflicts and skipping the temp folder itself."""
#     os.makedirs(temp_folder, exist_ok=True)
#     for item in os.listdir(base_path):
#         item_path = os.path.join(base_path, item)
#         if item == os.path.basename(temp_folder):  # Skip the temp folder itself
#             continue

#         temp_item_path = os.path.join(temp_folder, item)
#         if os.path.exists(temp_item_path):
#             # Handle conflicts by appending a number to the filename
#             i = 1
#             while os.path.exists(f"{temp_item_path}_{i}"):
#                 i += 1
#             temp_item_path = f"{temp_item_path}_{i}"
#         shutil.move(item_path, temp_item_path)  # Use the adjusted path
#     print(f"Existing files moved to temporary folder: {temp_folder}")

def move_existing_files_to_temp(base_path, temp_folder):
    """
    Moves existing files to a temporary folder, handling conflicts and skipping the temp folder itself.
    Only files are moved; directories are not affected.
    """
    os.makedirs(temp_folder, exist_ok=True)
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if item == os.path.basename(temp_folder) or not os.path.isfile(item_path):  # Skip the temp folder and directories
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


def get_new_directory_structure(client, files_with_summaries):
    system_msg = """You are an AI assistant that helps generate a directory structure for a software project.
                    You will receive a summary of the entire project, with descriptions of each file.
                    Your task is to generate an appropriate directory structure for the project, considering its content and context.
                    Ensure to include directories for scripts, tests, output, configuration, and documentation (like README.md and other docs).
                    The structure should be returned as a JSON object with appropriate folder and file names.
                    If you are creating a file that does not exist in the provided list, please provide the file's content as well."""

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

def combine_all_files(base_folder, extensions=None):
    """
    Combine the contents of specific file types within a directory structure.
    Args:
    base_folder (str): The base directory from which to start combining files.
    extensions (list): List of file extensions to include (e.g., ['.py', '.md']).
    """
    if extensions is None:
        extensions = ['.py', '.md']  # Default file types to combine if none specified

    combined_content = ""
    for root, _, files in os.walk(base_folder):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):  # Check if the file has a desired extension
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
        print(f"Files in {root}: {files}")
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

    # base_path = "Directory_Organizer/Test_Dir/Coding_Project_Summarizer"
    base_path = "Directory_Organizer/Test_Dir/GearGenerator"
    temp_folder = os.path.join(base_path, "temp_folder")
    
    # 1. Clean up any existing temp_folder to start fresh
    clean_up_temp_folder(temp_folder)

    # 2. Move existing files to the temp_folder
    move_existing_files_to_temp(base_path, temp_folder)
    
    combined_content = combine_all_files(temp_folder, extensions=['.py', '.md'])
    print(f"Combined Content:\n{combined_content}\n")
    
    # 3. Summarize the files now in the temp_folder
    project_summary = summarize_directory(temp_folder, ['.py', '.md'])
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
    
    # 9. Clean up the temp_folder
    clean_up_temp_folder(temp_folder)
    
    print("File relocation completed.")

unknown