import os

# Directory structure
project_root = "live_dialogue_options_project"
directories = {
    "data": ["preprocessed_audio", "raw_audio_samples"],
    "transcripts": [],
    "demos": [],
    "documentation": [],
    "models": ["pretrained", "trained"],
    "outputs": ["logs", "results"],
    "src": ["dialogue_suggestions", "diarization", "audio", "ui"],
    "utils": [],
    "tests": [],
    "assets": []
}

# Create sample files for each directory
sample_files = {
    "data": "sample_data.txt",
    "transcripts": "sample_transcript.txt",
    "demos": "demo_script.py",
    "documentation": "sample_doc.md",
    "models": "sample_model.txt",
    "outputs": "sample_output.txt",
    "src": "sample_code.py",
    "utils": "utility_script.py",
    "tests": "test_script.py",
    "assets": "sample_asset.txt"
}

for main_dir, subdirs in directories.items():
    path = os.path.join(project_root, main_dir)
    
    # Create sample file for the main directory
    if sample_files.get(main_dir):
        with open(os.path.join(path, sample_files[main_dir]), "w") as f:
            f.write(f"This is a sample file for {main_dir}.\n")
    
    # Create sample files for subdirectories
    for subdir in subdirs:
        sub_path = os.path.join(path, subdir)
        with open(os.path.join(sub_path, f"sample_for_{subdir}.txt"), "w") as f:
            f.write(f"This is a sample file for {subdir} under {main_dir}.\n")

print("Sample files created successfully!")
