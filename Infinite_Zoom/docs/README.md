# Infinite Zoom Transition Video Generator

This project uses various libraries including OpenCV, PIL, and Google Cloud Vision API to generate a zoom transition video between images.

## Description

This script (`infinite_zoom_2.py`) automates the creation of infinite zoom videos by generating keyframe transitions with descriptive image modifications. The main functionalities include:

1. **convertToTranspPNG**: Converts an image to a transparent PNG by setting black color as transparent.
2. **generate_image_description**: Uses Google Cloud Vision API and OpenAI to generate a descriptive sentence about an image.
3. **expand_image**: Resizes and scales an image, then uses OpenAI’s Image API to create an edited version based on a prompt.
4. **fill_center_of_image**: Crops and scales an image, fills the center, and uses the OpenAI Image API to generate a new edited version.
5. **generate_input_img_descriptions**: Generates and saves descriptions for images in a given directory.
6. **generate_keyframe_transition_frames**: Generates frames for a smooth transition between two keyframes using zooming.
7. **delete_all_frames**: Deletes all image frames in a specified directory.
8. **strip_to_numbers**: Helper function to extract and return numbers from text (used for sorting).
9. **generate_video_frames**: Uses keyframes to generate all video frames given specific parameters (fps, duration).
10. **make_video_from_frames**: Converts generated frames into a video file (AVI format).
11. **make_mp4_video_from_frames**: Converts generated frames into an MP4 video.
12. **get_session_path**: Constructs a session path based on a session number.
13. **delete_directory**: Deletes a specified directory recursively.
14. **rename_session_folders**: Renames session folders in numerical order.
15. **bridge_the_gap**: Bridges the gap between two images by creating an intermediate frame.
16. **generate_transition_keyframes**: Creates a series of keyframes to transition between a start and end image.

## Usage

To use the script, follow these steps:

1. Define paths and configuration constants such as `PARENT_PATH`, `INPUT_PATH`, `SESSIONS_PATH`, `TEMP_PATH`, `START_IMG`, and `END_IMG`.
2. Ensure API keys and paths are correctly set for Google Cloud Vision and OpenAI services.
3. Run the script to generate image descriptions, transition frames, and the final video.

## Dependencies

- os
- openai
- random
- time
- json
- pickle
- numpy
- PIL
- cv2
- requests
- moviepy
- glob
- shutil
- Google Cloud Vision API
- OpenAI API

Ensure all dependencies are installed and properly configured before running the script.

