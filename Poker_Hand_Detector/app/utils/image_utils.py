import cv2
import numpy as np
from mss import mss
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def resize_image(image, width=None, height=None):
    """
    Resize an image to the specified width and height.

    :param image: Image to resize.
    :param width: New width of the image.
    :param height: New height of the image.
    :return: Resized image.
    """
    try:
        if width is None and height is None:
            return image
        h, w = image.shape[:2]
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))
        resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        logging.info(f"Image resized to {dim[0]}x{dim[1]} successfully.")
        return resized_image
    except Exception as e:
        logging.error("Error resizing image: ", exc_info=True)
        return None

def preprocess_image(image):
    """
    Preprocess the image for card detection.

    :param image: Image to preprocess.
    :return: Preprocessed image.
    """
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)
        logging.info("Image preprocessed successfully.")
        return thresh
    except Exception as e:
        logging.error("Error preprocessing image: ", exc_info=True)
        return None

def crop_image(image, left, top, right, bottom):
    """
    Crop an image to the specified dimensions.

    :param image: Image to crop.
    :param left: The left margin of the cropping box.
    :param top: The top margin of the cropping box.
    :param right: The right margin of the cropping box.
    :param bottom: The bottom margin of the cropping box.
    :return: Cropped image.
    """
    try:
        cropped_image = image[top:bottom, left:right]
        logging.info("Image cropped successfully.")
        return cropped_image
    except Exception as e:
        logging.error("Error cropping image: ", exc_info=True)
        return None

def screen_capture(save_path='screenshot.png'):
    """
    Capture the screen and save it to a file.

    :param save_path: Path where the screenshot will be saved.
    :return: None
    """
    try:
        with mss() as sct:
            sct.shot(output=save_path)
            logging.info(f"Screen captured successfully and saved to {save_path}.")
    except Exception as e:
        logging.error("Error capturing screen: ", exc_info=True)

def load_image(image_path):
    """
    Load an image from a file.

    :param image_path: Path to the image file.
    :return: Loaded image.
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Image at {image_path} could not be loaded.")
        logging.info(f"Image loaded from {image_path} successfully.")
        return image
    except Exception as e:
        logging.error("Error loading image: ", exc_info=True)
        return None

def capture_screen(image_path):
    """
    Placeholder function to simulate screen capture.
    In a real-world scenario, this function would capture the screen or load an image for processing.

    :param image_path: Path to the image file. INPUT_REQUIRED {Provide the path to the image you want to process}
    :return: Loaded image.
    """
    try:
        # Simulate screen capture by loading an image from the given path
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Image at {image_path} could not be loaded.")
        logging.info(f"Simulated screen capture and loaded image from {image_path} successfully.")
        return image
    except Exception as e:
        logging.error("Error simulating screen capture: ", exc_info=True)
        return None