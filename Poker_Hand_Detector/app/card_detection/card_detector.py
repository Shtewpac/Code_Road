import cv2
import numpy as np
import os
from utils.image_utils import resize_image, preprocess_image
from config import RANK_IMAGES_PATH, SUIT_IMAGES_PATH

class CardDetector:
    def __init__(self):
        self.rank_images = self.load_images(RANK_IMAGES_PATH)
        self.suit_images = self.load_images(SUIT_IMAGES_PATH)

    def load_images(self, path):
        images = {}
        for filename in os.listdir(path):
            if filename.endswith(".png") or filename.endswith(".jpg"):
                img = cv2.imread(os.path.join(path, filename), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    key = os.path.splitext(filename)[0]
                    images[key] = img
        return images

    def find_contours(self, image):
        # Convert image to grayscale and apply threshold
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def match_template(self, image, template):
        # Perform template matching and return the best match
        res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        return max_val

    def detect_card(self, image):
        # Example implementation for detecting a single card
        contours = self.find_contours(image)
        for contour in contours:
            # Assuming contour processing and card extraction logic here
            pass
        # Further processing and template matching logic here

# Example usage
if __name__ == "__main__":
    detector = CardDetector()
    # Load an example image for demonstration purposes
    # Note: Replace 'example_image.jpg' with the path to an actual image file for testing
    img = cv2.imread('./assets/example_image.jpg')
    detector.detect_card(img)