# Configuration settings for the Poker Hand Detector application.

import os
import logging

# Base directory for project assets and configurations. 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths to directories containing rank and suit images
RANK_IMAGES_PATH = os.path.join(BASE_DIR, "assets/rank_images/")
SUIT_IMAGES_PATH = os.path.join(BASE_DIR, "assets/suit_images/")

# Detection thresholds and other constants
TEMPLATE_MATCHING_THRESHOLD = 0.8  # Set the threshold value for template matching accuracy.

# Other potentially adjustable settings for future implementation
SCREENSHOT_SAVE_PATH = os.path.join(BASE_DIR, "screenshots/")  # Directory to save screenshots if required
LOGGING_LEVEL = "INFO"  # Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE_PATH = os.path.join(BASE_DIR, "logs/poker_hand_detector.log")  # Path to log file

# Logging configuration
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

try:
    logger.info("Loading configuration settings for Poker Hand Detector.")
except Exception as e:
    logger.error("Error loading configuration settings: %s", e, exc_info=True)