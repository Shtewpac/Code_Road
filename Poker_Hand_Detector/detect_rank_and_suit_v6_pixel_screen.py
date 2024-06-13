import os
import cv2
import numpy as np
import mss
import pygetwindow as gw
import time
import subprocess
# from poker_logic import *
from enum import Enum
from collections import Counter
from google.cloud import vision
from adbnativeblitz import AdbFastScreenshots


### Constants ###
BKG_THRESH = -50
CARD_THRESH = 140
CORNER_WIDTH = 56
CORNER_HEIGHT = 160
RANK_WIDTH = 150
RANK_HEIGHT = 200
SUIT_WIDTH = 70
SUIT_HEIGHT = 100
RANK_DIFF_MAX = 3000
SUIT_DIFF_MAX = 700
CARD_MAX_AREA = 120000
CARD_MIN_AREA = 10000
DEFAULT_WIDTH = 755
DEFAULT_HEIGHT = 422

font = cv2.FONT_HERSHEY_SIMPLEX

# bounding_boxes_data = {
#     'Table Card 1': {'Rank Bounding Box': ((300, 364), (404, 501)), 'Suit Bounding Box': ((305, 508), (391, 604))},
#     'Table Card 2': {'Rank Bounding Box': ((574, 366), (678, 490)), 'Suit Bounding Box': ((576, 502), (666, 619))},
#     'Table Card 3': {'Rank Bounding Box': ((852, 364), (957, 492)), 'Suit Bounding Box': ((847, 506), (937, 605))},
#     'Table Card 4': {'Rank Bounding Box': ((1123, 363), (1234, 502)), 'Suit Bounding Box': ((1117, 519), (1206, 613))},
#     'Table Card 5': {'Rank Bounding Box': ((1397, 365), (1508, 498)), 'Suit Bounding Box': ((1398, 523), (1488, 608))},
    
#     'Hand 1 Card 1': {'Rank Bounding Box': ((286, 814), (403, 944)), 'Suit Bounding Box': ((308, 956), (413, 1051))},
#     'Hand 1 Card 2': {'Rank Bounding Box': ((443, 797), (541, 926)), 'Suit Bounding Box': ((438, 955), (531, 1057))},
#     'Hand 2 Card 1': {'Rank Bounding Box': ((1260, 793), (1363, 923)), 'Suit Bounding Box': ((1262, 937), (1355, 1055))},
#     'Hand 2 Card 2': {'Rank Bounding Box': ((1410, 792), (1494, 921)), 'Suit Bounding Box': ((1382, 933), (1480, 1050))},
# }

bounding_boxes_data = {
    'Table Card 1': {'Rank Bounding Box': ((18, 7), (82, 71)), 'Suit Bounding Box': ((17, 80), (66, 138))},
    'Table Card 2': {'Rank Bounding Box': ((165, 6), (219, 72)), 'Suit Bounding Box': ((166, 89), (211, 137))},
    'Table Card 3': {'Rank Bounding Box': ((314, 5), (365, 74)), 'Suit Bounding Box': ((316, 79), (363, 137))},
    'Table Card 4': {'Rank Bounding Box': ((463, 7), (518, 72)), 'Suit Bounding Box': ((465, 79), (509, 134))},
    'Table Card 5': {'Rank Bounding Box': ((612, 5), (667, 73)), 'Suit Bounding Box': ((612, 86), (660, 145))},
    
    'Hand 1 Card 1': {'Rank Bounding Box': ((5, 220), (66, 315)), 'Suit Bounding Box': ((22, 323), (76, 386))},
    'Hand 1 Card 2': {'Rank Bounding Box': ((90, 237), (146, 309)), 'Suit Bounding Box': ((92, 313), (136, 368))},
    'Hand 2 Card 1': {'Rank Bounding Box': ((539, 238), (589, 308)), 'Suit Bounding Box': ((539, 318), (588, 379))},
    'Hand 2 Card 2': {'Rank Bounding Box': ((617, 231), (669, 302)), 'Suit Bounding Box': ((589, 300), (655, 365))},
}


class Query_card:
    """Structure to store information about query cards in the camera image."""

    def __init__(self):
        self.contour = [] # Contour of card
        self.width, self.height = 0, 0 # Width and height of card
        self.corner_pts = [] # Corner points of card
        self.center = [] # Center point of card
        self.warp = [] # 200x300, flattened, grayed, blurred image
        self.rank_img = [] # Thresholded, sized image of card's rank
        self.suit_Zimg = [] # Thresholded, sized image of card's suit
        self.best_rank_match = "Unknown" # Best matched rank
        self.best_suit_match = "Unknown" # Best matched suit
        self.rank_diff = 0 # Difference between rank image and best matched train rank image
        self.suit_diff = 0 # Difference between suit image and best matched train suit image


class ImageProcessor:
    @staticmethod
    # Function to resize the image to specific dimensions
    def resize_image(image, width=None, height=None):
        # Get the dimensions of the image
        h, w = image.shape[:2]
        
        # Determine the new dimensions
        if width is None and height is None:
            return image
        elif width is None:
            aspect_ratio = height / h
            dim = (int(aspect_ratio * w), height)
        else:
            aspect_ratio = width / w
            dim = (width, int(aspect_ratio * h))
        
        # Resize the image
        resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        
        return resized

    @staticmethod
    # Function to capture the screen of a specific application window
    def capture_screen(window_title):
        # Find the window with the specified title
        window = gw.getWindowsWithTitle(window_title)[0]
        
        # Get the window dimensions
        left, top, right, bottom = window.left, window.top, window.right, window.bottom
        
        with mss.mss() as sct:
            # Capture the screen of the selected window
            monitor = {"top": top, "left": left, "width": right - left, "height": bottom - top}
            screen = sct.grab(monitor)
            
            # Convert the screen to a numpy array
            screen = np.array(screen)
            
            # Convert the color space from BGR to RGB
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
            
        return screen

    @staticmethod
    # Function to load an image from a file
    def load_image(image_path):
        # Load the image from the file
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    @staticmethod
    def crop_image_top_bottom(img):
        # Get the height and width of the image
        height, width = img.shape[:2]

        # Determine the top 20% and bottom 30%
        top = int(height * 0.10)
        bottom = int(height * 0.90)

        # Crop the image
        cropped_img = img[top:bottom, :]

        return cropped_img
    
    @staticmethod
    def crop_image_borders(img):
        # Crop the top and bottom by 10% of the image height
        cropped_img = ImageProcessor.crop_image_top_bottom(img)
        # crop the left and right by 2% of the image width
        cropped_img = cropped_img[:, int(cropped_img.shape[1] * 0.02):int(cropped_img.shape[1] * 0.98)]
        return cropped_img
    
    @staticmethod
    def crop_black_borders(image):
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Threshold the image to create a binary image where white is the content and black are the borders
        _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        
        # Find the contours of the regions with content
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find the bounding box that contains all contours
        x_min, y_min, x_max, y_max = np.inf, np.inf, 0, 0
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            x_min = min(x, x_min)
            y_min = min(y, y_min)
            x_max = max(x + w, x_max)
            y_max = max(y + h, y_max)
        
        # Crop the image using the bounding box
        cropped_image = image[y_min:y_max, x_min:x_max]
        
        return cropped_image

    @staticmethod
    # Function to print the locations of the bounding boxes
    def print_bounding_box_locations(bounding_boxes):
        for i, (start, end) in enumerate(bounding_boxes):
            print(f"Bounding Box {i+1}: Start: {start}, End: {end}")

    @staticmethod
    # Function to get the list of open application windows
    def get_open_windows():
        windows = gw.getAllWindows()
        window_titles = [window.title for window in windows if window.title]
        return window_titles

    @staticmethod
    # Function to draw bounding boxes on the image based on the bounding box data
    def draw_bounding_boxes_from_data(image, bounding_boxes_data):
        for key, value in bounding_boxes_data.items():
            rank_start, rank_end = value['Rank Bounding Box']
            suit_start, suit_end = value['Suit Bounding Box']
            
            cv2.rectangle(image, rank_start, rank_end, (0, 255, 0), 2)
            cv2.rectangle(image, suit_start, suit_end, (0, 0, 255), 2)
            
            cv2.putText(image, key, (rank_start[0], rank_start[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    @staticmethod
    # Function to preprocess the image
    def preprocess_image(image):
        """Returns a grayed, blurred, and adaptively thresholded image."""
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        
        # Show the blurred image
        # cv2.imshow("Blurred Image", blur)
        
        img_w, img_h = np.shape(image)[:2]
        bkg_level = gray[int(img_h/100)][int(img_w/2)]
        thresh_level = bkg_level + BKG_THRESH

        retval, thresh = cv2.threshold(blur, thresh_level, 255, cv2.THRESH_BINARY_INV)
        
        # Show the thresholded image
        # cv2.imshow("Thresholded Image", thresh)
        
        cropped_thresh = thresh
        # Find the largest contour in the cropped thresholded image and crop the image to the bounds of the largest contour
        contours, _ = cv2.findContours(cropped_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) != 0:
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Show the largest contour in a separate window
            # cv2.imshow("Largest Contour", cv2.drawContours(image.copy(), [largest_contour], -1, (0, 255, 0), 2))
            # cv2.waitKey(0)
            
            x, y, w, h = cv2.boundingRect(largest_contour)
            # Show the largest contour in a separate window
            # cv2.imshow("Largest Contour", cv2.drawContours(image.copy(), [largest_contour], -1, (0, 255, 0), 2))
            # cv2.waitKey(0)
            
            # Crop the image to the bounds of the largest contour
            cropped_thresh = cropped_thresh[y:y+h, x:x+w]
            
        
        # Show the cropped image
        # cv2.imshow("Cropped Thresh Image", cropped_thresh)
        # cv2.waitKey(0)
        
        # Find the largest contour in the cropped thresholded image
        contours, _ = cv2.findContours(cropped_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) != 0:
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Show the largest contour in a separate window
            # cv2.imshow("Largest Contour", cv2.drawContours(image.copy(), [largest_contour], -1, (0, 255, 0), 2))
            # cv2.waitKey(0)
            
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Crop the image to the bounds of the largest contour
            cropped_thresh = cropped_thresh[y:y+h, x:x+w]
        
        # Show the cropped image
        # cv2.imshow("Cropped Image", cropped_thresh)
                
        return cropped_thresh

class Train_ranks:
    def __init__(self):
        self.img = []
        self.name = "Placeholder"

class Train_suits:
    def __init__(self):
        self.img = []
        self.name = "Placeholder"

class CardDetector:
    @staticmethod
    def load_ranks(filepath):
        """Loads rank images from directory specified by filepath. Stores
        them in a list of Train_ranks objects."""

        train_ranks = []
        i = 0
        
        for Rank in ['Ace','Two','Three','Four','Five','Six','Seven',
                    'Eight','Nine','Ten','Jack','Queen','King']:
            train_ranks.append(Train_ranks())
            train_ranks[i].name = Rank
            filename = Rank + '.jpg'
            full_path = os.path.join(filepath, filename)
            
            if os.path.exists(full_path):
                train_ranks[i].img = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)
                if train_ranks[i].img is None:
                    print("Failed to load image file:", full_path)
            else:
                print("Image file not found:", full_path)
            
            i = i + 1

        return train_ranks

    @staticmethod
    def load_suits(filepath):
        """Loads suit images from directory specified by filepath. Stores
        them in a list of Train_suits objects."""

        train_suits = []
        i = 0
        
        for Suit in ['Spades','Diamonds','Clubs','Hearts']:
            train_suits.append(Train_suits())
            train_suits[i].name = Suit
            filename = Suit + '.jpg'
            train_suits[i].img = cv2.imread(filepath+filename, cv2.IMREAD_GRAYSCALE)
            i = i + 1

        return train_suits
    
def match_card(qCard, train_ranks, train_suits):
    """Finds best rank and suit matches for the query card. Differences
    the query card rank and suit images with the train rank and suit images.
    The best match is the rank or suit image that has the least difference."""

    best_rank_match_diff = 10000
    best_suit_match_diff = 10000
    best_rank_match_name = "Unknown"
    best_suit_match_name = "Unknown"
    i = 0

    if (len(qCard.rank_img) != 0) and (len(qCard.suit_img) != 0):
        
        # Difference the query card rank image from each of the train rank images,
        # and store the result with the least difference
        for Trank in train_ranks:
            # Resize the query card rank image to match the size of the train rank image
            qCard.rank_img_resized = cv2.resize(qCard.rank_img, (Trank.img.shape[1], Trank.img.shape[0]))
            
            # Show the resized rank image
            # cv2.imshow("Rank Image Resized", qCard.rank_img_resized)
            # cv2.waitKey(0)
            
            diff_img = cv2.absdiff(qCard.rank_img_resized, Trank.img)
            rank_diff = int(np.sum(diff_img)/255)
            
            if rank_diff < best_rank_match_diff:
                # Show the best rank difference image
                best_rank_match_diff = rank_diff
                best_rank_match_name = Trank.name
                
                # Show the best rank difference image
                # cv2.imshow("Best Rank Difference Image", best_rank_diff_img)
                # cv2.imshow("Best Rank Match", Trank.img)
                # cv2.imshow("Query Rank Image", qCard.rank_img_resized)
                # cv2.waitKey(0)
                
            
        
        # Same process with suit images
        for Tsuit in train_suits:
            # Resize the query card suit image to match the size of the train suit image
            qCard.suit_img_resized = cv2.resize(qCard.suit_img, (Tsuit.img.shape[1], Tsuit.img.shape[0]))
            
            # Show the resized suit image
            # cv2.imshow("Suit Image Resized", qCard.suit_img_resized)
            # cv2.waitKey(0)
            
            diff_img = cv2.absdiff(qCard.suit_img_resized, Tsuit.img)
            suit_diff = int(np.sum(diff_img)/255)
            
            if suit_diff < best_suit_match_diff:
                # Show the best suit difference image
                best_suit_match_diff = suit_diff
                best_suit_match_name = Tsuit.name
            
                # cv2.imshow("Best Suit Difference Image", best_suit_diff_img)
                # cv2.imshow("Best Suit Match", Tsuit.img)
                # cv2.imshow("Query Suit Image", qCard.suit_img_resized)
                # cv2.waitKey(0)
                
        
    rank_code = rank_name_to_code(best_rank_match_name) if best_rank_match_name != "Unknown" else "U"
    if rank_code == "U":
        rank_text = perform_ocr(qCard.rank_img)
        print("RANK_TEXT", rank_text)
    suit_code = best_suit_match_name[0] if best_suit_match_name != "Unknown" else "U"
    
    return rank_code + suit_code

def perform_ocr(image):
    """Performs OCR on the given image using Google Cloud Vision API."""
    client = vision.ImageAnnotatorClient()
    _, encoded_image = cv2.imencode('.jpg', image)
    content = encoded_image.tobytes()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return texts[0].description
    else:
        return ""



def rotate_bounding_box(bbox, angle):
    """Rotates a bounding box by the specified angle."""
    center_x = (bbox[0][0] + bbox[1][0]) // 2
    center_y = (bbox[0][1] + bbox[1][1]) // 2
    
    # Calculate the new coordinates of the bounding box corners after rotation
    corners = np.array([[bbox[0][0], bbox[0][1]],
                        [bbox[1][0], bbox[0][1]],
                        [bbox[1][0], bbox[1][1]],
                        [bbox[0][0], bbox[1][1]]])
    
    rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), angle, 1.0)
    rotated_corners = cv2.transform(np.array([corners]), rotation_matrix)[0]
    
    # Find the new bounding box coordinates after rotation
    min_x = np.min(rotated_corners[:, 0])
    min_y = np.min(rotated_corners[:, 1])
    max_x = np.max(rotated_corners[:, 0])
    max_y = np.max(rotated_corners[:, 1])
    
    rotated_bbox = ((int(min_x), int(min_y)), (int(max_x), int(max_y)))
    return rotated_bbox

def rotate_image(image, angle):
    """Rotates an image by the specified angle."""
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    # try:
    try:
        rotated_image = cv2.warpAffine(image, rotation_matrix, (w, h))
    except cv2.error as e:
        print("Error rotating image:", e)
        return image
    return rotated_image

class HandType(Enum):
    HIGH_CARD = 1
    PAIR = 2 
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

def get_best_hand(cards):
    # Sort cards by rank
    cards.sort(key=lambda x: x.rank, reverse=True)
    
    # Check for flush
    flush = all(card.suit == cards[0].suit for card in cards)
    
    # Check for straight
    ranks = [card.rank for card in cards]
    straight = len(set(ranks)) == 5 and max(ranks) - min(ranks) == 4
    
    # Check for straight flush
    if flush and straight:
        if ranks[0] == 14: # Ace high straight flush
            return HandType.ROYAL_FLUSH, cards[:5] 
        else:
            return HandType.STRAIGHT_FLUSH, cards[:5]
    
    # Check for four of a kind
    rank_counts = Counter(ranks)
    if 4 in rank_counts.values():
        quad_rank = [rank for rank, count in rank_counts.items() if count == 4][0]
        kicker = [card for card in cards if card.rank != quad_rank][0]
        return HandType.FOUR_OF_A_KIND, [card for card in cards if card.rank == quad_rank] + [kicker]
    
    # Check for full house
    if 3 in rank_counts.values() and 2 in rank_counts.values():
        trip_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
        pair_rank = [rank for rank, count in rank_counts.items() if count == 2][0]
        return HandType.FULL_HOUSE, [card for card in cards if card.rank == trip_rank] + [card for card in cards if card.rank == pair_rank][:2]
    
    # Check for flush
    if flush:
        return HandType.FLUSH, cards[:5]
    
    # Check for straight
    if straight:
        return HandType.STRAIGHT, cards[:5]
    
    # Check for three of a kind
    if 3 in rank_counts.values():
        trip_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
        kickers = [card for card in cards if card.rank != trip_rank][:2]
        return HandType.THREE_OF_A_KIND, [card for card in cards if card.rank == trip_rank] + kickers
    
    # Check for two pair
    if list(rank_counts.values()).count(2) == 2:
        pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]
        kicker = [card for card in cards if card.rank not in pair_ranks][0]
        return HandType.TWO_PAIR, [card for card in cards if card.rank in pair_ranks][:4] + [kicker]
    
    # Check for pair
    if 2 in rank_counts.values():
        pair_rank = [rank for rank, count in rank_counts.items() if count == 2][0]
        kickers = [card for card in cards if card.rank != pair_rank][:3]
        return HandType.PAIR, [card for card in cards if card.rank == pair_rank] + kickers
    
    # High card
    return HandType.HIGH_CARD, cards[:5]

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

def rank_name_to_code(rank_name):
    rank_map = {
        'Ace': 'A', 'King': 'K', 'Queen': 'Q', 'Jack': 'J', 'Ten': 'T',
        'Nine': '9', 'Eight': '8', 'Seven': '7', 'Six': '6', 'Five': '5', 'Four': '4', 'Three': '3', 'Two': '2'
    }
    return rank_map.get(rank_name, 'U')

def string_to_card(card_code):
    rank_map = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}
    suit_map = {'S': 'Spades', 'D': 'Diamonds', 'C': 'Clubs', 'H': 'Hearts'}

    rank = rank_map.get(card_code[0])
    suit = suit_map.get(card_code[1])

    if rank and suit:
        return Card(rank, suit)
    else:
        print(f"Invalid card code: {card_code}")
        return None

def name_to_card(name):
    rank_map = {
        'Ace': 14, 'King': 13, 'Queen': 12, 'Jack': 11, 'Ten': 10,
        'Nine': 9, 'Eight': 8, 'Seven': 7, 'Six': 6, 'Five': 5, 'Four': 4, 'Three': 3, 'Two': 2
    }
    suit_map = {
        'Spades': 'S', 'Diamonds': 'D', 'Clubs': 'C', 'Hearts': 'H'
    }
    try:
        rank = rank_map[name.split()[0]]
        suit = suit_map[name.split()[2]]
        return Card(rank, suit)
    except KeyError:
        print(f"Unrecognized card name: {name}")
        # Handle the error appropriately - perhaps by skipping this card or using a default value
        return None
    # return Card(rank, suit)
    
def extract_card_images(image_resized, value):
    # Extract rank and suit images based on bounding box coordinates
    rank_start, rank_end = value['Rank Bounding Box']
    suit_start, suit_end = value['Suit Bounding Box']

    # Crop and preprocess rank and suit images
    rank_img = image_resized[rank_start[1]:rank_end[1], rank_start[0]:rank_end[0]]
    suit_img = image_resized[suit_start[1]:suit_end[1], suit_start[0]:suit_end[0]]

    rank_img_processed = ImageProcessor.preprocess_image(rank_img)
    suit_img_processed = ImageProcessor.preprocess_image(suit_img)

    return rank_img_processed, suit_img_processed

def compare_and_announce_winner(hand1_cards, hand2_cards, table_cards):
    best_hand1_type, _ = get_best_hand(hand1_cards + table_cards)
    best_hand2_type, _ = get_best_hand(hand2_cards + table_cards)

    if best_hand1_type.value > best_hand2_type.value:
        print(f"Hand 1 wins with a {best_hand1_type.name}")
        return 'hand1'
    elif best_hand1_type.value < best_hand2_type.value:
        print(f"Hand 2 wins with a {best_hand2_type.name}")
        return 'hand2'
    else:
        # Return the hand with the highest card 
        hand1_max_rank = max([card.rank for card in hand1_cards])
        hand2_max_rank = max([card.rank for card in hand2_cards])
        
        if hand1_max_rank > hand2_max_rank:
            print(f"Hand 1 wins with a {best_hand1_type.name} and a higher card")
            return 'hand1'
        elif hand1_max_rank < hand2_max_rank:
            print(f"Hand 2 wins with a {best_hand2_type.name} and a higher card")
            return 'hand2'
        else:
            print("It's a tie!")
            return 'tie'


def draw_winning_hand_boxes(image, winning_hand_keys):
    for key in winning_hand_keys:
        value = bounding_boxes_data[key]
        rank_start, rank_end = value['Rank Bounding Box']
        suit_start, suit_end = value['Suit Bounding Box']
        
        # Draw a bounding box around both the rank and the suit
        cv2.rectangle(image, rank_start, rank_end, (0, 0, 255), 3)
        cv2.rectangle(image, suit_start, suit_end, (0, 0, 255), 3)

def display_detected_cards(image_resized, bounding_boxes_data, hand1_cards, hand2_cards, table_cards):
    rank_map = {
        14: 'Ace', 13: 'King', 12: 'Queen', 11: 'Jack', 10: 'Ten',
        9: 'Nine', 8: 'Eight', 7: 'Seven', 6: 'Six', 5: 'Five',
        4: 'Four', 3: 'Three', 2: 'Two'
    }

    all_cards = hand1_cards + hand2_cards + table_cards
    
    for key, value in bounding_boxes_data.items():
        rank_bbox = value['Rank Bounding Box']
        suit_bbox = value['Suit Bounding Box']
        
        # Find the corresponding Card object based on the key
        if 'Hand 1' in key:
            card_index = int(key[-1]) - 1
            card = hand1_cards[card_index]
        elif 'Hand 2' in key:
            card_index = int(key[-1]) - 1
            card = hand2_cards[card_index]
        else:  # Table cards
            card_index = int(key[-1]) - 1
            card = table_cards[card_index]
        
        # Get the rank name from the rank_map dictionary
        best_rank_match = rank_map.get(card.rank, 'Unknown')
        best_suit_match = card.suit
        
        # Calculate the center point of the rank bounding box
        center_point = (
            (rank_bbox[0][0] + rank_bbox[1][0]) // 2,
            (rank_bbox[0][1] + rank_bbox[1][1]) // 2
        )
        
        # Draw the detected rank and suit on the image
        cv2.putText(image_resized, best_rank_match + " of " + best_suit_match, center_point, 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.circle(image_resized, center_point, 5, (0, 255, 0), -1)

    # After drawing, display the image
    # Resize the image to fit the screen
    image_resized = ImageProcessor.resize_image(image_resized, height=800)
    cv2.imshow("Detected Cards", image_resized)
    

def find_image_bounds(image):
    # Crop the image by 20% from all sides
    cropped_img = image[int(image.shape[0] * 0.2):int(image.shape[0] * 0.8), int(image.shape[1] * 0.2):int(image.shape[1] * 0.8)]
    image = cropped_img
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    
    img_w, img_h = np.shape(image)[:2]
    bkg_level = gray[int(img_h/100)][int(img_w/2)]
    thresh_level = bkg_level + CARD_THRESH

    retval, thresh = cv2.threshold(blur, thresh_level, 255, cv2.THRESH_BINARY)
    
    # Show the thresholded image
    # cv2.imshow("Thresholded Image", thresh)
    # cv2.waitKey(0)
    
    # Find the 5 largest contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:7]
    
    # Draw the contours on the image
    # cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
    
    # Show the image with the contours
    # cv2.imshow("Image with Contours", image)
    # cv2.waitKey(0)ss
    
    # Crop the image to the bounds of the 7 largest contours
    x, y, w, h = cv2.boundingRect(cv2.convexHull(np.concatenate(contours)))
    
    # contours = contours[2:]
    # x,y,w2,h2 = cv2.boundingRect(cv2.convexHull(np.concatenate(contours)))
    cropped_image = image[y:y+h, x:x+w]
    
    # Show the cropped image
    # cv2.imshow("Cropped Image", cropped_image)
    # cv2.waitKey(0)
    
    # Save the cropped image to a file
    cv2.imwrite("cropped_image.png", cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR))
    
    return cropped_image
    

def main():
    start_tapping = False
    path = os.path.dirname(os.path.abspath(__file__))

    # Load the train ranks and suits
    train_ranks = CardDetector.load_ranks(path + '/Card_Imgs/')
    train_suits = CardDetector.load_suits(path + '/Card_Imgs/')
    
    # Set the path to your ADB executable
    adb_path = r"W:\\Downloads\\scrcpy-win64-v2.4\\scrcpy-win64-v2.4\\adb.exe"
    
    # Set the serial number of your Android device
    device_serial = "29141FDH300KJX"

    # Set the desired width and height of the captured screen
    width = 1600
    height = 900

    # Set the bitrate for screen recording
    bitrate = "20M"
    
    
    # Load screen.png image
    # image = ImageProcessor.load_image("screen.png")
    # find_image_bounds(image)
    
    with AdbFastScreenshots(
        adb_path=adb_path,
        device_serial=device_serial,
        time_interval=179,
        width=width,
        height=height,
        bitrate=bitrate,
        use_busybox=False,
        connect_to_device=True,
        screenshotbuffer=10,
        go_idle=0,
    ) as adbscreen:
        for image in adbscreen:
            # Display the captured screen using OpenCV
            # cv2.imshow("Android Screen", image)
            # cv2.waitKey(1)
            
            # # Save the image to a file
            # cv2.imwrite("screen.png", cv2.cvtColor(image_cropped, cv2.COLOR_RGB2BGR))
            
            # Check for '0' key press to start tapping
            key = cv2.waitKey(1) & 0xFF
            if key == ord('0'):
                start_tapping = True
                print("Starting to tap...")
                
            image_cropped = find_image_bounds(image)
            
            # Resize the cropped image
            image_resized = ImageProcessor.resize_image(image_cropped, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT)
            
            # Save the resized image to a file
            # cv2.imwrite("resized_image.png", cv2.cvtColor(image_resized, cv2.COLOR_RGB2BGR))
            
            # Overlqy the bounding boxes on the image
            for key, value in bounding_boxes_data.items():
                rank_start, rank_end = value['Rank Bounding Box']
                suit_start, suit_end = value['Suit Bounding Box']
                
                cv2.rectangle(image_resized, rank_start, rank_end, (0, 255, 0), 2)
                cv2.rectangle(image_resized, suit_start, suit_end, (0, 0, 255), 2)
                
                cv2.putText(image_resized, key, (rank_start[0], rank_start[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Display the image with the bounding boxes
            cv2.imshow("Detected Cards", image_resized)
            
            
            hand1 = []
            hand2 = []
            table_cards = []
            
            # Detect cards and ranks inside each bounding box
            for key, value in bounding_boxes_data.items():
                rank_bbox = value['Rank Bounding Box']
                suit_bbox = value['Suit Bounding Box']
                
                # Rotate the bounding box coordinates for specific cards
                if key == 'Hand 1 Card 1':
                    rank_bbox = rotate_bounding_box(rank_bbox, -10)  # Rotate 10 degrees clockwise
                    suit_bbox = rotate_bounding_box(suit_bbox, -10)
                elif key == 'Hand 2 Card 2':
                    rank_bbox = rotate_bounding_box(rank_bbox, 10)  # Rotate 10 degrees counterclockwise
                    suit_bbox = rotate_bounding_box(suit_bbox, 10)
                
                # Extract the rank and suit regions from the resized image using the rotated bounding box coordinates
                rank_img = image_resized[rank_bbox[0][1]:rank_bbox[1][1], rank_bbox[0][0]:rank_bbox[1][0]]
                suit_img = image_resized[suit_bbox[0][1]:suit_bbox[1][1], suit_bbox[0][0]:suit_bbox[1][0]]
                
                # Rotate the rank and suit images for specific cards
                if key == 'Hand 1 Card 1':
                    rank_img = rotate_image(rank_img, -10)  # Rotate 10 degrees clockwise
                    suit_img = rotate_image(suit_img, -10)
                elif key == 'Hand 2 Card 2':
                    rank_img = rotate_image(rank_img, 10)  # Rotate 10 degrees counterclockwise
                    suit_img = rotate_image(suit_img, 10)
                
                # Preprocess the rank and suit images
                try:
                    rank_img_processed = ImageProcessor.preprocess_image(rank_img)
                    suit_img_processed = ImageProcessor.preprocess_image(suit_img)
                except cv2.error as e:
                    print("Error preprocessing image:", e)
                    continue
                
                # Create a Query_card object and set its rank and suit images
                qCard = Query_card()
                qCard.rank_img = rank_img_processed
                qCard.suit_img = suit_img_processed
                
                # Match card and standardize output
                card_code = match_card(qCard, train_ranks, train_suits)
                
                # Skip if card detection fails
                if 'U' in card_code:
                    print(f"Card detection failed for {key}. Skipping...")
                    continue
                
                # Append detected card to the appropriate list
                if 'Hand 1' in key:
                    hand1.append(card_code)
                elif 'Hand 2' in key:
                    hand2.append(card_code)
                else:  # Table cards
                    table_cards.append(card_code)
            
            # Only proceed if all cards are successfully detected
            if len(hand1) + len(hand2) + len(table_cards) < 9:
                print("Incomplete card detection. Retrying...")
                continue
            
            # Convert card codes to Card objects
            hand1_cards = [string_to_card(code) for code in hand1]
            hand2_cards = [string_to_card(code) for code in hand2]
            table_cards = [string_to_card(code) for code in table_cards]
            
            # Compare hands
            winning_hand = compare_and_announce_winner(hand1_cards, hand2_cards, table_cards)

            # if winning_hand != 'tie':
            #     winning_hand_keys = ['Hand 1 Card 1', 'Hand 1 Card 2'] if winning_hand == 'hand1' else ['Hand 2 Card 1', 'Hand 2 Card 2']
            #     draw_winning_hand_boxes(image_resized, winning_hand_keys)
            
            if winning_hand != 'tie':
                winning_hand_keys = ['Hand 1 Card 1', 'Hand 1 Card 2'] if winning_hand == 'hand1' else ['Hand 2 Card 1', 'Hand 2 Card 2']
                # Calculate the center coordinates of the winning hand
                winning_hand_bbox = bounding_boxes_data[winning_hand_keys[0]]['Rank Bounding Box']
                x = (winning_hand_bbox[0][0] + winning_hand_bbox[1][0]) // 2
                y = (winning_hand_bbox[0][1] + winning_hand_bbox[1][1]) // 2
                
                # Scale the coordinates to match the device screen resolution
                device_width = 1600
                device_height = 900
                x_scaled = int(x * device_width / DEFAULT_WIDTH)
                y_scaled = int(y * device_height / DEFAULT_HEIGHT)
                
                # if start_tapping:
                #     # Send the tap command using ADB
                #     tap_command = f"{adb_path} -s {device_serial} shell input tap {x_scaled} {y_scaled}"
                #     subprocess.run(tap_command, shell=True)
                #     # wait for 1 second
                #     time.sleep(0.1)   
                    
            # Display detected cards
            print("Bounding Boxes Data:", bounding_boxes_data)
            display_detected_cards(image_resized, bounding_boxes_data, hand1_cards, hand2_cards, table_cards)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    # Clean up
    cv2.destroyAllWindows()



if __name__ == "__main__":
    main()