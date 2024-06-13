import cv2
from card_detection.card_detector import CardDetector
from hand_analysis.hand_evaluator import HandEvaluator
from config import logger
from utils.image_utils import capture_screen

def main():
    try:
        # Initialize the card detector and hand evaluator
        card_detector = CardDetector()
        hand_evaluator = HandEvaluator()

        # Capture or load an image (for the sake of example, we'll define a placeholder function to simulate image capture)
        image_path = "Poker_Hand_Detector/tests/test_imgs/1.png"  # INPUT_REQUIRED {path_to_the_image_for_analysis}
        image = capture_screen(image_path)  # This should be replaced with actual image capture logic

        # Detect cards in the image
        detected_cards = card_detector.detect_cards(image)
        if not detected_cards:
            logger.info("No cards detected.")
            return

        # Evaluate the poker hand from detected cards
        hand_result = hand_evaluator.evaluate_hand(detected_cards)
        logger.info(f"Detected hand: {hand_result}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()