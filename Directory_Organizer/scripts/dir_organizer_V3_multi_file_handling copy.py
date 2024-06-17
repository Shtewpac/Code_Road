import os
import shutil
import openai
from openai import OpenAI
import json
import time
import re


FILES_WITH_SUMMARIES = """File: Dir_Summarizer_V1.py
Summary: This script is designed to summarize software projects using OpenAI's API. Below is a high-level summary of its functionality and structure:

**Project Title:** Software Project Summarizer

**Project Description:**
* The script aims to automate the summarization of software projects by combining relevant files and utilizing OpenAI's API to generate concise summaries of the project's documentation and code.       
* It is intended for developers or teams who need to quickly understand the essence of a software project without manually parsing through extensive documentation and codebases.
* The main problem it solves is the time-consuming task of manually creating comprehensive summaries from fragmented project documentation.
* The script's unique approach leverages OpenAI's advanced language model capabilities to produce detailed summaries in a structured and organized format.

**Key Features/Functionalities:**
* Combines the contents of `.py` and `.md` files from a specified directory.
* Splits the combined content into manageable chunks to efficiently interact with the OpenAI API.
* Automatically handles API rate limits by incorporating a retry mechanism after a delay.
* Saves the generated summary to a Markdown file (`Project_Summaries.md`).

**Technical Overview:**
* **Programming Languages:** Python
* **Libraries/Frameworks:**
  * `os` for file handling and directory traversal.
  * `openai` for interacting with the OpenAI API.
  * `time` for managing delays.
* **Architecture:** The script follows a procedural approach with clear separation of concerns, dividing the main functions into file handling, text chunking, interaction with the OpenAI API, and file saving.
* **Algorithms:** The script uses simple text chunking based on a fixed chunk size to manage API limitations effectively.

**Code Structure (Optional):**
* **Main Modules/Classes/Files:**
  * `combine_files(directory, extensions)`: Combines contents of specified file types.
  * `split_into_chunks(text, chunk_size)`: Splits text into smaller chunks.
  * `summarize_text(client, text_chunk, chunk_index)`: Interacts with OpenAI API to summarize text chunks.
  * `save_to_md(file_path, content)`: Saves the summary to a Markdown file.
  * `main(directory)`: Orchestrates the execution flow of the script.

**Additional Notes (Optional):**
* The script includes basic error handling for file reading and API interactions.
* Future enhancements could include support for additional file types or directories, improved error handling, and customization options for the summary format.
* It assumes the presence of an OpenAI API key and appropriate permissions to read files from the specified directories.

This summary provides an overview of the script's purpose, key features, and technical specifications, making it easier for new developers or stakeholders to understand its functionality and usage.    

File: Dir_Summarizer_V2.py
Summary: This script is a utility for summarizing code and technical documentation found within a specified root directory. The main functions and features of the script are outlined below:

**Project Title:** Code and Documentation Summarizer

**Project Description:**
- The primary purpose of this project is to automate the process of summarizing software projects using OpenAI's language model.      
- It targets developers and project managers who need concise overviews of code repositories and technical documentation.
- The project addresses the need for quick comprehension and documentation of software projects, saving manual effort and time.       
- The unique approach leverages the OpenAI API to generate human-like summaries, combining and processing large chunks of text efficiently.

**Key Features/Functionalities:**
- **File Combination:** Aggregates the content of files with specified extensions from a directory, handling subdirectories while ignoring virtual environment folders.
- **Text Chunking:** Divides large text into manageable chunks to comply with API constraints.
- **OpenAI Interaction:** Uses the OpenAI API to generate summaries for each text chunk while managing rate limits gracefully.        
- **Markdown Summarization:** Appends detailed summaries to a Markdown file, distinguishing different project insights clearly.       
- **Error Handling:** Implements robust error handling for file operations and API interactions.

**Technical Overview:**
- **Programming Languages:** Python
- **Libraries/Frameworks:**
  - `openai` for interacting with the OpenAI API
  - `os` for file system operations
  - `time` for handling delays
- **Architecture:** The script is organized procedurally with modular functions for readability and maintainability.
- **Algorithms (if applicable):** Not explicitly detailed, but includes text chunking and API interaction retry logic.

**Code Structure (Optional):**
- Main modules include:
  - `combine_files(directory, extensions)`: Combines the contents of files from a directory.
  - `split_into_chunks(text, chunk_size)`: Splits text into chunks.
  - `summarize_text(client, text_chunk, chunk_index)`: Sends text chunks to OpenAI for summarization.
  - `save_to_md(root_directory, content)`: Saves the summary content to a Markdown file.
  - `summarize_directory(root_directory, directory, extensions)`: Processes each subdirectory for summarization.
  - `main(root_directory)`: Drives the script's flow by iterating over directories and invoking summarization functions.

**Additional Notes (Optional):**
- **Potential areas for improvement or future enhancements:**      
  - Integrate more sophisticated file type detection.
  - Implement a graphical user interface for ease of use.
  - Allow for more flexible configuration options via a configuration file or command-line arguments.
- **Known limitations or challenges:**
  - Handling extremely large projects could still pose performance and API rate limit issues.
  - The quality of summaries depends heavily on OpenAI's model performance and limitations.

This script aims to streamline the task of project summarization, making it easier to understand and document software projects.      

File: Dir_Summarizer_V3.py
Summary: This Python script is designed to automate the summarization of software projects by analyzing their technical documentation and code. Here is a brief summary of the key functionalities and components of the script:

**Project Title:** Coding Project Summarizer

**Project Description:**
* This project aims to generate concise summaries of software projects from their technical documentation and source code.
* The summaries are intended for developers, project managers, or stakeholders who need an overview of multiple projects quickly.     
* It addresses the challenge of manually reading and understanding extensive project documentation and codebases.

**Key Features/Functionalities:**
* Combines content from specified file extensions (e.g., `.py`, `.md`) in the given directories.
* Splits the combined content into manageable chunks.
* Uses OpenAI's API to generate summaries for each chunk and then combines them into a final summary.
* Saves the summarized content into a single markdown file.        

**Technical Overview:**
* **Programming Languages:** Python
* **Libraries/Frameworks:**
  - `os`: For file and directory manipulation.
  - `openai`: To interact with the OpenAI API for generating summaries.
  - `time`: For handling retries with delays.
* **Architecture:** The script operates as a client-server where the client is the summarization script, and the server is the OpenAI service.
* **Algorithms (if applicable):**
  - Chunking algorithm to split text into specified sizes.
  - Retry mechanism to handle API rate limits.

**Code Structure (High-Level Overview):**
* **Combine_files:** Collects content from specified file extensions within a directory.
* **Split_into_chunks:** Divides combined content into chunks of specified size.
* **Summarize_text:** Sends text chunks to the OpenAI API for summarization, with retry logic for rate limits.
* **Save_to_md:** Appends the generated summaries to a markdown file.
* **Summarize_directory:** Orchestrates the complete summarization process for a given directory.
* **Main function:** Initializes the program, clears old summaries, and processes each sub-directory that isn't a virtual environment.

**Additional Notes:**
* The script includes robust error handling and retry logic to deal with API rate limits and file reading errors.
* Future enhancements could include parallel processing of chunks, support for more file types, and an improved user interface for specifying input parameters.

File: Dir_Summarizer_V4_Version_Analysis.py
Summary: This is a Python script designed to summarize software projects by analyzing their technical documentation and code files. Below is a brief summary of the script:

**Project Title:** Software Project Summarizer

**Project Description:**
* The main goal of this project is to automate the summarization of software projects by analyzing technical documentation and code files.
* It is targeted at developers or teams who need concise summaries of multiple projects.
* The script aims to solve the time-consuming task of manually summarizing project details, providing a streamlined and efficient alternative.
* The unique approach involves leveraging OpenAI's API to generate summaries, which ensures high-quality, context-aware output.       

**Key Features/Functionalities:**
* Combines content from multiple files within a specified directory.
* Splits combined content into manageable chunks before summarization.
* Utilizes OpenAI's API to generate summaries for each chunk.      
* Aggregates chunk summaries into a final comprehensive summary.   
* Saves the final summary to a Markdown file for easy readability and sharing.
* Handles various file extensions (e.g., .py, .md) and excludes common virtual environment directories (e.g., venv, env).

**Technical Overview:**
* **Programming Languages:** Python
* **Libraries/Frameworks:**
  * `os`: For file and directory handling.
  * `time`: For managing retry delays.
  * `openai`: For interacting with the OpenAI API to generate summaries.
* **Architecture:** Script-based automation with a focus on modular functions for combining files, splitting text, summarizing chunks, and saving output.
* **Algorithms:** N/A

**Code Structure:**
* **File Handling Functions:** Responsible for combining files and splitting text into chunks.
* **OpenAI Interaction:** Summarizes text chunks using the OpenAI API, with built-in retry logic for handling rate limits.
* **File Saving Function:** Appends the final summary to a Markdown file.
* **Directory Summarization Function:** Aggregates content from directories and processes it for summarization.
* **Main Program Logic:** Controls the overall flow, including clearing existing summary files and iterating over project directories.

**Additional Notes:**
* **Future Enhancements:**
  * Add support for additional file types and extensions.
  * Improve handling of large files or directories.
  * Enhance error handling and logging mechanisms.
* **Dependencies:**
  * Requires an OpenAI API key for functionality.
  * Relies on external libraries (`openai`, `os`, `time`).

This script is a powerful tool for developers seeking to quickly summarize and document multiple software projects."""

API_KEY = "<YOUR_API_KEY>"
CHUNK_SIZE = 64000  # Adjust chunk size as needed
CHUNK_SUMMARY_SYSTEM_MSG = "You are an AI assistant skilled at summarizing software projects from technical documentation and code. Analyze the provided text (which may be a fragment of a larger project) and generate a brief summary."
FINAL_SUMMARY_SYSTEM_MSG = "You are an AI assistant skilled at summarizing software projects from technical documentation and code. Analyze the provided text (which may be a fragment of a larger project) and generate a brief summary."

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
        print("API Response:", response)
        
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
     # files_with_summaries = ""
    # for root, _, files in os.walk(temp_path):
    #     for file_name in files:
    #         file_path = os.path.join(root, file_name)
    #         with open(file_path, "r") as f:
    #             file_content = f.read()
    #         file_summary = summarize_text(client, file_content, 1, CHUNK_SUMMARY_SYSTEM_MSG)
    #         relative_path = os.path.relpath(file_path, temp_path)
    #         files_with_summaries += f"File: {relative_path}\nSummary: {file_summary}\n\n"
    files_with_summaries = FILES_WITH_SUMMARIES
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

    # # 4. Summarize the files now in the temp_folder
    # project_summary = summarize_directory(temp_folder, ['.py', '.md']) 
    # print(f"Project Summary:\n{project_summary}\n")

    # 5. Relocate and rename the files from the temp_folder to the new structure in base_path
    relocate_and_rename_files(temp_folder, base_path, PROJECT_STRUCTURE, client)  
    
    # # 6. Clean up the temp_folder
    # clean_up_temp_folder(temp_folder)
    
    print("File relocation completed.")
unknown