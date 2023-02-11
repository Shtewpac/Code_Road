"""
What this code does:
Takes an audio file or transcribed text and generates an animation that corresponds to the text to help explain the information to visual learners

How this is accomplished:
- If the user gives the program an audio file the program will generate an image of each concept described in the audiofile and play the image over that
segment of time in the audio file where it is being described
- If the user provides a text input, first the code will determine whether the information is described in a straightforward, easy to comprehend way. 
    - If the text is not described in a good way, then the program will rephrase the text in a comprehensible and readable way.
- Then the code will take the now readable text and generate a voice to read it.
- The code then generates the video   
"""

import os
import ast
import openai
import requests
import json
import speech_recognition as sr
# import ffmpeg
# from pydub import AudioSegment

import transcript

openai.api_key = "<your key here>"

CUR_WORKING_DIR = os.path.dirname(__file__) + "/"
SESSIONS_PATH = CUR_WORKING_DIR + "sessions/"
INPUT_PATH = CUR_WORKING_DIR + "input/"

def generate_img(prompt):    
    # The API endpoint for DALL-E
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
        )

    # Get the URL of the generated image
    image_url = response['data'][0]['url']

    # Print the URL of the generated image
    return image_url

# Function to transcribe audio file with timestamps
def transcribe_audio(file_path):
    # Initialize recognizer class
    r = sr.Recognizer()
    # Load audio file
    audio = sr.AudioFile(file_path)
    # Open audio file and transcribe with timestamps
    with audio as source:
        audio_data = r.record(source)
        transcript = r.recognize_google(audio_data, show_all=True)
        print("transcript:",transcript); print("\n\n")

def strip_to_numbers(e):
    num = int(''.join(filter(str.isdigit, e)))
    # print("new num:",num)
    return num

def rename_session_folders():
    folder_names = os.listdir(SESSIONS_PATH)
    folder_names.sort(key=strip_to_numbers)
    for n in range(len(folder_names)):
        old_session_name = SESSIONS_PATH + folder_names[n]
        new_session_name = SESSIONS_PATH + "session" + str(n)
        print("old_session_name:",old_session_name)
        print("new_session_name:",new_session_name)
        os.rename(old_session_name, new_session_name)

# Example usage
# transcribe_audio('Visual_Learner/input/Dec_of_Indep_2.wav')

my_transcript = transcript.the_transcript 
print("my_transcript:\n",my_transcript,"\n")

transcript_paragraph = ""
for timestamp, string in my_transcript:
    transcript_paragraph += string + " "
# print("transcript_paragraph:\n",transcript_paragraph,"\n")

ideas_list_prompt = (f"separate this text into singular ideas give your answer as a python list of (timestamp,idea) tuples using the list with (timestamp,string) tuples, dont include the word answer: in your response: \n\n paragraph: {transcript_paragraph} \n\n timestamps list: {my_transcript}")
# Generate the text
completions = openai.Completion.create(engine="text-davinci-003", prompt=ideas_list_prompt, max_tokens=3000)
ideas = completions.choices[0].text.strip().strip("Answer:").strip("answer:").strip().strip('[').strip(')]')
print("ideas:\n",ideas)
ideas_list = []
for idea in ideas.split("), "):
    print(idea)
    new_item = eval(idea+")")
    print("new_item:",new_item)
    ideas_list.append(new_item)
print("ideas_list:\n",ideas_list)


fps = 24
sessionNum = len(os.listdir(SESSIONS_PATH))
session_path = SESSIONS_PATH + "session" + str(sessionNum) + "/"
gen_path = session_path + "generations/"
out_path = session_path + "output/"
rename_session_folders()
os.mkdir(session_path)
os.mkdir(gen_path)
for timestamp,idea in ideas_list:
    # print("(timestamp,idea):",(timestamp,idea))
    print("idea:",idea)
    idea_to_img_prompt = (f"If you were to create an image to summarize the following idea, what would the image look like? Give your answer as a direct description of the image: \n\n idea: {idea}")
    print("idea_to_img_prompt:",idea_to_img_prompt)
    completions = openai.Completion.create(engine="text-davinci-003", prompt=idea_to_img_prompt, max_tokens=3000)
    img_prompt = completions.choices[0].text.strip().strip("Answer:").strip("answer:")
    print("img_prompt:",img_prompt)
    img_URL = generate_img(img_prompt)
    with open(CUR_WORKING_DIR+'image.jpg', 'wb') as f:
        f.write(requests.get(img_URL).content)


# img_URL = generate_img("physical map of North America shown with a red star over Virginia and a label on the star reading Jamestown in bold letters.")
# with open(CUR_WORKING_DIR+'image.jpg', 'wb') as f:
#     f.write(requests.get(img_URL).content)
