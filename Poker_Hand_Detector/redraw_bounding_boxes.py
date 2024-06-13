import cv2
import numpy as np

# Your bounding box data
bounding_boxes_data = {
    'Table Card 1': {'Rank Bounding Box': ((300, 364), (404, 501)), 'Suit Bounding Box': ((305, 508), (391, 604))},
    'Table Card 2': {'Rank Bounding Box': ((574, 366), (678, 490)), 'Suit Bounding Box': ((576, 502), (666, 619))},
    'Table Card 3': {'Rank Bounding Box': ((852, 364), (957, 492)), 'Suit Bounding Box': ((847, 506), (937, 605))},
    'Table Card 4': {'Rank Bounding Box': ((1123, 363), (1234, 502)), 'Suit Bounding Box': ((1117, 519), (1206, 613))},
    'Table Card 5': {'Rank Bounding Box': ((1397, 365), (1508, 498)), 'Suit Bounding Box': ((1398, 523), (1488, 608))},
    'Hand 1 Card 1': {'Rank Bounding Box': ((286, 814), (403, 944)), 'Suit Bounding Box': ((308, 956), (413, 1051))},
    'Hand 1 Card 2': {'Rank Bounding Box': ((443, 797), (541, 926)), 'Suit Bounding Box': ((438, 955), (531, 1057))},
    'Hand 2 Card 1': {'Rank Bounding Box': ((1260, 793), (1363, 923)), 'Suit Bounding Box': ((1262, 937), (1355, 1055))},
    'Hand 2 Card 2': {'Rank Bounding Box': ((1410, 792), (1494, 921)), 'Suit Bounding Box': ((1382, 933), (1480, 1050))}
}

# Load your image
image = cv2.imread('resized_image.png')

# Global variables
drawing = False
start_point = None
end_point = None

# Function to handle mouse events
def mouse_callback(event, x, y, flags, param):
    global drawing, start_point, end_point, image_copy
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            image_copy = image.copy()
            cv2.rectangle(image_copy, start_point, (x, y), (0, 255, 0), 2)
            cv2.imshow('Image', image_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)
        image_copy = image.copy()
        cv2.rectangle(image_copy, start_point, end_point, (0, 255, 0), 2)
        cv2.imshow('Image', image_copy)

# Create a window and set the mouse callback
cv2.namedWindow('Image')
cv2.setMouseCallback('Image', mouse_callback)

# Iterate over each label and redraw the bounding boxes
for label, boxes in bounding_boxes_data.items():
    for box_type, box_coords in boxes.items():
        print(f"Redraw the bounding box for {label} - {box_type}")
        # Display the image and wait for user input
        cv2.imshow('Image', image)
        cv2.waitKey(0)
        # Update the bounding box coordinates
        bounding_boxes_data[label][box_type] = (start_point, end_point)

# Print the updated bounding boxes
print("Updated Bounding Boxes:")
for label, boxes in bounding_boxes_data.items():
    print(f"{label}:")
    for box_type, box_coords in boxes.items():
        print(f"  {box_type}: {box_coords}")

# Close the window
cv2.destroyAllWindows()