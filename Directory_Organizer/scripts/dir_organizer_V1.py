import os
import shutil
import openai
from openai import OpenAI
import json

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

client = OpenAI(api_key="<YOUR_API_KEY>")

def create_file(file_path, content=''):
    with open(file_path, 'w') as f:
        f.write(content)

def move_existing_files_to_temp(base_path, temp_folder):
    os.makedirs(temp_folder, exist_ok=True)
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path):
            shutil.move(item_path, temp_folder)
        elif os.path.isfile(item_path):
            shutil.move(item_path, temp_folder)

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
    messages = [
        {"role": "system", "content": f"""You are an AI assistant that helps organize files within a software project's structure. 
                                         You will receive a summary of the entire project, a summary of a specific file, and the project's directory structure. 
                                         Your task is to determine the most appropriate location and name for this file within the project's directory structure, considering its content and context.

                                         Project Structure:
                                         {json.dumps(project_structure, indent=4)}"""},
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
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        functions=[function_call],
        function_call="auto" 
    )

    response_message = response.choices[0].message
    if response_message.get("function_call"):
        function_args = json.loads(response_message["function_call"]["arguments"])
        new_location = function_args["new_location"]
        new_file_name = function_args["new_file_name"]
        return new_location, new_file_name
    else:
        return None, None

def relocate_and_rename_file(file_path, new_location, new_file_name):
    new_file_path = os.path.join(new_location, new_file_name)
    # os.makedirs(new_location, exist_ok=True)
    shutil.move(file_path, new_file_path)
    print(f"File '{file_path}' moved to '{new_file_path}'")
    
def relocate_and_rename_files(base_path, project_summary, project_structure):
    for root, dirs, files in os.walk(base_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'r') as f:
                file_content = f.read()
            file_summary = file_content  # Use a snippet of the file content for summary
            new_location, new_file_name = get_file_relocation_info(client, project_summary, file_summary, project_structure)
            if new_location and new_file_name:
                relocate_and_rename_file(file_path, new_location, new_file_name)


def clean_up_temp_folder(temp_folder):
    shutil.rmtree(temp_folder)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python create_project_structure.py <directory_path>")
    else:
        base_path = sys.argv[1]
        temp_folder = os.path.join(base_path, "temp_folder")
        
        move_existing_files_to_temp(base_path, temp_folder)
        create_project_structure(base_path)
        project_summary = "This is a summary of the entire project."
        relocate_and_rename_files(base_path, project_summary, PROJECT_STRUCTURE)
        clean_up_temp_folder(temp_folder)

unknown