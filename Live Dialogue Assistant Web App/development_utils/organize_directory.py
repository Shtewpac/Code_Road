import os
import shutil

project_dir = "./LIVE_DIALOGUE_OPTIONS"

def remove_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)

def move_file(src, dest):
    if os.path.exists(src):
        shutil.move(src, dest)

def clear_cache(directory):
    pycache_path = os.path.join(directory, "__pycache__")
    remove_directory(pycache_path)

def add_to_gitignore(entry):
    with open(".gitignore", "a+") as f:
        if entry not in f.read():
            f.write(f"\n{entry}")

# 1. Remove OLD directory
remove_directory("./OLD")

# 2. Remove src_backups directory
remove_directory(os.path.join(project_dir, "src_backups"))

# 3. Clear out __pycache__ directories
for root, dirs, files in os.walk(project_dir):
    for d in dirs:
        if d == "__pycache__":
            clear_cache(os.path.join(root, d))

# 4. Move utility scripts to development_utils
if not os.path.exists(os.path.join(project_dir, "development_utils")):
    os.mkdir(os.path.join(project_dir, "development_utils"))

utilities = ["create_project_directory_2.py", "create_dir_sample_files.py", 
             "src_code_combine_to_single_file.py", "combined_src.py", "print_directory_tree.py"]

for utility in utilities:
    move_file(os.path.join(project_dir, "misc", utility), os.path.join(project_dir, "development_utils"))

# 5. Move set_system_path.md to documentation
move_file(os.path.join(project_dir, "misc", "set_system_path.md"), os.path.join(project_dir, "documentation"))

# 6. Remove empty directories (in this case, directories not mentioned in the list)
# You can add directories to this list as you find them.
empty_dirs = ["transcripts", "utils"]
for directory in empty_dirs:
    remove_directory(os.path.join(project_dir, directory))

# 7. Check for .env in .gitignore and add if not present
add_to_gitignore(".env")

print("Directory reorganization complete!")
