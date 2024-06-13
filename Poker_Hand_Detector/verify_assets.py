import os
import logging
from pathlib import Path

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, filename='assets_verification.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define the expected naming convention for suit and rank images
expected_ranks = ['two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'jack', 'queen', 'king', 'ace']
expected_suits = ['hearts', 'diamonds', 'clubs', 'spades']
expected_extensions = ['.jpg', '.png']

# Paths to the asset directories
rank_images_path = Path('./assets/rank_images/')
suit_images_path = Path('./assets/suit_images/')

def verify_images(directory, expected_names):
    """
    Verifies that all expected images exist in the directory and adhere to the naming convention.
    """
    missing_files = []
    incorrect_format_files = []

    # List all files in the directory
    actual_files = [f.name for f in directory.iterdir() if f.is_file()]

    # Check each expected file
    for name in expected_names:
        matching_files = [f for f in actual_files if f.startswith(name) and any(f.endswith(ext) for ext in expected_extensions)]
        if not matching_files:
            missing_files.append(name)
        else:
            for file in matching_files:
                if not any(file.endswith(ext) for ext in expected_extensions):
                    incorrect_format_files.append(file)

    # Log findings
    if missing_files:
        logging.warning(f"Missing files in {directory}: {missing_files}")
    else:
        logging.info(f"All expected files found in {directory}.")

    if incorrect_format_files:
        logging.warning(f"Files with incorrect format in {directory}: {incorrect_format_files}")
    else:
        logging.info(f"All files in {directory} have the correct format.")

def main():
    logging.info("Starting verification of asset images.")

    try:
        # Verify rank images
        verify_images(rank_images_path, expected_ranks)

        # Verify suit images
        verify_images(suit_images_path, expected_suits)

        logging.info("Asset verification completed successfully.")
    except Exception as e:
        logging.error("An error occurred during asset verification.", exc_info=True)

if __name__ == "__main__":
    main()