import os
import openai
import random
import time
import json
import pickle
from PIL import Image
import cv2
import requests
import numpy as np
import glob
import shutil
import moviepy.video.io.ImageSequenceClip
import tempfile
import io


from random import random
from random import randint
from time import sleep
from typing import Dict, List
from datetime import datetime
from datetime import timedelta

from google.cloud import vision

OPENAI_API_KEY = "<your api key here>"
openai.api_key = OPENAI_API_KEY

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'G:\My Drive\Instagram Bot\instagrapi-master\My_Projects\key.json'

output_imgs = []

def convertToTranspPNG(img):
    rgba = img.convert("RGBA")
    datas = rgba.getdata()
    newData = []
    for item in datas:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:  # finding black colour by its RGB value
            # storing a transparent value when we find a black colour
            newData.append((255, 255, 255, 0))
        else: newData.append(item)  # other colours remain unchanged
    rgba.putdata(newData)
    # rgba.save(img_path, "PNG")
    return rgba

def generate_image_description(img_url):
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = img_url
    vision_response = client.label_detection(image=image)
    # print('Labels (and confidence score):')
    # print('=' * 30)
    # for label in vision_response.label_annotations:
    #     print(label.description, '(%.2f%%)' % (label.score*100.))

    text_prompt = "make a likely guess as to what a photo contains given the following identified attributes with confidence scores:"
    for label in vision_response.label_annotations:
        text_prompt += "\n" + label.description + ' ' + ('(%.2f%%)' % (label.score*100.))
    text_prompt += "\nand output your answer as a single sentence describing the photo, starting with the phrase: \"A photo of \""
    # print("text_prompt:\n",text_prompt)
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=text_prompt,
        temperature=0,
        max_tokens=40,
    )
    resp = ""
    for r in response['choices']:
        resp = r['text'].split('\n')[-1]
    return resp.strip('A photo of').strip('\"')

def expand_image(img_path, scale_factor, img_prompt, output_path):
    # Open the image file and get its size
    image = Image.open(img_path)
    img_size = image.size

    # Calculate the scale factor and the scaled-down size of the image
    sf = 1024 / max(img_size)
    scaled_down_size = (int(sf * img_size[0] / scale_factor), int(sf * img_size[1] / scale_factor))

    # Resize the image to the scaled-down size
    scaled_down_image = image.resize(scaled_down_size)

    # Create a transparent PNG image and paste the scaled-down image onto it
    image_mask = convertToTranspPNG(Image.new("RGB", (1024, 1024), (0, 0, 0)))
    # image_mask.paste(scaled_down_image, (int(1024/2 - scaled_down_size[0]/2), int(1024/2 - scaled_down_size[1]/2)))
    image_mask.paste(scaled_down_image, ((1024 - scaled_down_size[0]) // 2, (1024 - scaled_down_size[1]) // 2))

    # Save the image_mask image to the temporary file
    mask_path = TEMP_PATH + "image_mask.png"
    image_mask.save(mask_path,"PNG")

    # Use OpenAI's Image API to create an edited version of the image
    response = openai.Image.create_edit(
        image=open(mask_path, "rb"),
        mask=open(mask_path, "rb"),
        prompt=img_prompt,
        n=1,
        size="1024x1024",
    )

    # Save the edited image to a file and append it to a list of output images
    output_img = Image.open(io.BytesIO(requests.get(response["data"][0]["url"]).content))
    output_imgs.append({"img": output_img, "url": response["data"][0]["url"]})
    
    # genNum = len(os.listdir(gen_path))+1
    # generated_img_path = gen_path + "generatedImg" + str(genNum) + '.png'
    generated_img_path = output_path
    output_img.save(generated_img_path,"PNG")
    # Return the path to the output image and the URL of the output image
    print("url:",response["data"][0]["url"])
    return generated_img_path, response["data"][0]["url"]

def fill_center_of_image(img_path, scale_factor, edge_percent, img_prompt, output_path):
    # Open the image file and get its size
    # temp_img_path = TEMP_PATH + "temp_fill_img.png"
    # expand_image(img_path,1.0,"",temp_img_path)
    image = Image.open(img_path)
    img_size = image.size
    print("img_size:",img_size)
    
    crop_size = (int(scale_factor * max(img_size)),int(scale_factor * max(img_size)))
    print("crop_size:",crop_size)
    w,h = img_size
    cropped_square = image.crop(((w-crop_size[0])//2,(h-crop_size[1])//2,(w+crop_size[0])//2,(h+crop_size[1])//2))
    
    cropped_scaled_square = cropped_square.resize((1024,1024))
    empty_square_size = int(1024 * (1-edge_percent))
    square_img_arr = np.array(cropped_scaled_square)
    w,h = cropped_scaled_square.size
    square_img_arr[(h-empty_square_size)//2 : (h+empty_square_size)//2, (w-empty_square_size)//2 : (w+empty_square_size)//2] = (0, 0, 0)
    image_mask = Image.fromarray(square_img_arr)
    image_mask = convertToTranspPNG(image_mask)
    mask_path = TEMP_PATH + "image_mask.png"
    image_mask.save(mask_path,"PNG")

    # Use OpenAI's Image API to create an edited version of the image
    response = openai.Image.create_edit(
        image=open(mask_path, "rb"),
        mask=open(mask_path, "rb"),
        prompt=img_prompt,
        n=1,
        size="1024x1024",
    )

    # Save the edited image to a file and append it to a list of output images
    generated_img = Image.open(io.BytesIO(requests.get(response["data"][0]["url"]).content))
    # output_imgs.append({"img": generated_img, "url": response["data"][0]["url"]})
    scaled_down_gen_img = generated_img.resize(crop_size)
    w,h = img_size
    image.paste(scaled_down_gen_img,((w-crop_size[0])//2,(h-crop_size[1])//2))
    image.save(output_path,"PNG")
    if img_size != (1024,1024):
        expand_image(output_path,1.0,"anything",output_path)
    # Return the path to the output image and the URL of the output image
    print("url:",response["data"][0]["url"])
    return generated_img, response["data"][0]["url"]




def generate_input_img_descriptions(input_path):
    input_img_fnames = filter(lambda f: (".jpg" or ".png") in f, os.listdir(input_path))
    description_dict = {}
    with open(input_path + 'image_descriptions.txt', 'w') as f:
        for img_fname in input_img_fnames:
            img_path,img_URL = expand_image(input_path+img_fname,1.0,"no prompt")
            img_description = generate_image_description(img_URL)
            # print("img_fname:",img_fname,"")
            print(img_fname,"---",img_description)
            description_dict[img_fname] = [img_URL,img_description]
        # print("description_dict:",description_dict)
        f.write(str(description_dict))

def generate_keyframe_transition_frames(frames_per_keyframe, keyframe1_path, keyframe2_path):
    zoom_factor = np.linspace(1.0, scale_factor, num=frames_per_keyframe)
    image1 = Image.open(keyframe1_path)
    image2 = Image.open(keyframe2_path)
    image2 = image2.resize((int(scale_factor * image2.size[0]), int(scale_factor * image2.size[1])))
    w,h = image2.size
    frame_list = []
    for zoom in zoom_factor:
        temp_image1 = image1.resize((int(zoom * image1.size[0]), int(zoom * image1.size[1])))
        temp_image2 = image2.resize((int(zoom * image2.size[0]), int(zoom * image2.size[1])))
        tw,th = temp_image2.size
        temp_image2.paste(temp_image1, ((tw - temp_image1.size[0]) // 2, (th - temp_image1.size[1]) // 2))
        temp_image2 = temp_image2.crop(((tw - w)//2, (th - h)//2, (tw + w)//2, (th + h)//2))
        temp_image2 = temp_image2.resize((1024,1024))
        frame_list.append(temp_image2)
    return frame_list


def delete_all_frames(frame_path):
    frames_list = glob.glob(frame_path+'*.jpg')
    for filename in frames_list:
        print("deleting:",filename)
        os.remove(filename)

def strip_to_numbers(e):
    num = int(''.join(filter(str.isdigit, e)))
    # print("new num:",num)
    return num

def generate_video_frames(fps,video_duration,keyframe_path,frame_out_path):
    try: os.mkdir(frame_out_path)
    except OSError as e:
        print("Failed to remove directory:",frame_out_path)
    delete_all_frames(frame_out_path) # Remove pre-existing frames
    # delete_all_frames(frame_out_path) 
    keyframe_names = os.listdir(keyframe_path)
    keyframe_names.sort(key=strip_to_numbers)
    num_keyframes = len(keyframe_names)
    # zoom_array = np.linspace(1.0, scale_factor*num_keyframes, num=frames_per_keyframe)
    # print("keyframe_names:",keyframe_names)
    
    print("num_keyframes:",num_keyframes)
    total_frames = video_duration * fps
    print("total_frames:",total_frames)
    while total_frames % (num_keyframes-1) != 0: total_frames += 1
    print("new total_frames:",total_frames) #256
    print("new video duration:",total_frames/fps)
    frames_per_keyframe = int(total_frames / (num_keyframes-1))
    print("frames_per_keyframe:",frames_per_keyframe)
    for i in range(num_keyframes-1):
        frame1_path = keyframe_path + keyframe_names[i]
        frame2_path = keyframe_path + keyframe_names[i+1]
        # print("frame1_path:",frame1_path)
        # print("frame2_path:",frame2_path)
        frames = generate_keyframe_transition_frames(frames_per_keyframe+1,frame1_path,frame2_path)
        print("frames in cur:",len(frames))
        for fi in range(frames_per_keyframe):
            frame_name = frame_out_path + "frame" + str((i+1)*(frames_per_keyframe) - fi) + ".jpg"
            frames[fi].save(frame_name,"JPEG")


def make_video_from_frames(frameSize,fps,frame_path,output_path): #create video from frames
    out_num = len(glob.glob(output_path+'*.avi')) + len(glob.glob(output_path+'*.mp4'))
    out = cv2.VideoWriter(output_path+'zoom_video_' + str(out_num) + '.avi',cv2.VideoWriter_fourcc(*'DIVX'), fps, frameSize)
    frames_list = glob.glob(frame_path+'*.jpg')
    frames_list.sort(key=strip_to_numbers)
    print("num video frames:",len(frames_list))
    for filename in frames_list:
        # print("filename:",filename)
        img = cv2.imread(filename)
        out.write(img)
    out.release()

def make_mp4_video_from_frames(fps,frame_path,output_path): #create video from frames
    out_num = len(glob.glob(output_path+'*.avi')) + len(glob.glob(output_path+'*.mp4'))
    frames_list = os.listdir(frame_path)
    frames_list.sort(key=strip_to_numbers)
    print("num video frames:",len(frames_list))
    image_files = [os.path.join(frame_path,img)
                for img in frames_list
                if img.endswith(".jpg")]
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
    clip.write_videofile(output_path+'zoom_video_' + str(out_num) + '.mp4')

def get_session_path(session_num):
    return SESSIONS_PATH + "session" + str(session_num) + "/"

def delete_directory(dir_path):
    print("Removing Directory:",dir_path)
    try: shutil.rmtree(dir_path)
    except OSError as e:
        print("Failed to remove directory:",dir_path)
        print("Error: %s - %s." % (e.filename, e.strerror))

def rename_session_folders():
    folder_names = os.listdir(SESSIONS_PATH)
    folder_names.sort(key=strip_to_numbers)
    for n in range(len(folder_names)):
        old_session_name = SESSIONS_PATH + folder_names[n]
        new_session_name = SESSIONS_PATH + "session" + str(n)
        print("old_session_name:",old_session_name)
        print("new_session_name:",new_session_name)
        os.rename(old_session_name, new_session_name)

# example_URL_1 = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-pjbTgqTb0wdiMhnQ3ZJloAsG/user-vtQYWlNqqks67d3wh4wlTO26/img-jNU3zOLiZVHD1GRSXukPGL3C.png?st=2023-01-02T23%3A43%3A21Z&se=2023-01-03T01%3A43%3A21Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-01-02T19%3A40%3A55Z&ske=2023-01-03T19%3A40%3A55Z&sks=b&skv=2021-08-06&sig=EMgrQ0wvKL6eysD5MGLAk1ScUGm95bOCLQGFp/6VMZs%3D"
# example_URL_2 = "https://hips.hearstapps.com/hmg-prod.s3.amazonaws.com/images/golden-retriever-royalty-free-image-506756303-1560962726.jpg?crop=0.672xw:1.00xh;0.166xw,0&resize=640:*"
# example_image_description_1 = generate_image_description(example_URL_1)
# example_image_description_2 = generate_image_description(example_URL_2)
# example_image_description = "a transition between " + example_image_description_1 + "and " + example_image_description_2
# print("example_image_description:",example_image_description); print()
# expand_image(START_IMG_PATH,1.25,example_image_description)

# generate_input_img_descriptions(INPUT_PATH)
# with open(INPUT_PATH + 'image_descriptions.txt') as f: data = f.read()
# input_description_dict = json.loads(data.replace("\'", "\""))
# print("input_description_dict:",input_description_dict)

  
def bridge_the_gap(keyframe1_path,keyframe2_path,scale_factor,output_path):
    image1 = Image.open(keyframe1_path)
    image2 = Image.open(keyframe2_path)
    image2 = image2.resize((int(scale_factor * image2.size[0]), int(scale_factor * image2.size[1])))
    w1,h1 = image1.size
    w2,h2 = image2.size
    wg_outer = (w2-w1)//2+w1
    wg_inner = int(w1/scale_factor)
    inner_cropped_img = image2
    img_arr = np.array(inner_cropped_img)
    img_arr[(h2-wg_outer)//2 : (h2+wg_outer)//2, (w2-wg_outer)//2 : (w2+wg_outer)//2] = (0, 0, 0)
    print("img_arr:",img_arr)
    # Creating an image out of the previously modified array
    inner_cropped_img = Image.fromarray(img_arr)
    inner_cropped_img = convertToTranspPNG(inner_cropped_img)
    outer_cropped_img = convertToTranspPNG(image1)
    outer_cropped_img = outer_cropped_img.crop(((w1-wg_inner)//2,(h1-wg_inner)//2, (w1+wg_inner)//2, (h1+wg_inner)//2))
    w1,h1 = outer_cropped_img.size
    # w2,h2 = inner_cropped_img.size
    # inner_cropped_img.paste(outer_cropped_img,(((w2-wg_outer)-w1)//2,((h2-wg_outer)-h1)//2))
    inner_cropped_img.paste(outer_cropped_img,((w2-wg_inner)//2,(h2-wg_inner)//2))
    # inner_cropped_img.paste(image1,(0,0))
    inner_cropped_img.save(output_path)
    expand_image(output_path,1.0,"Anything",output_path)
    

def generate_transition_keyframes(start_img_path,end_img_path,num_keyframes,scale_factor):
    # sessionNum = len(os.listdir(SESSIONS_PATH))
    # session_path = SESSIONS_PATH + "session" + str(sessionNum) + "/"
    # gen_path = session_path + "generations/"
    # out_path = session_path + "output/"
    try: os.mkdir(session_path)
    except OSError as e:
        rename_session_folders()
        os.mkdir(session_path)
        # print("Failed to remove directory:",frame_out_path)
    os.mkdir(gen_path); os.mkdir(out_path)
    img_prompt = "dream"
    # expand from start image
    num_outframes = 2
    connecting_prompt = "white background"
    genNum = len(os.listdir(gen_path))+1
    output_path = gen_path + "generatedImg" + str(genNum) + '.png'
    # img_path,img_URL = expand_image(start_img_path,1.0,img_prompt,output_path) # get starting URL
    # while(genNum < num_keyframes-num_outframes): 
    #     if (genNum > 0): img_prompt = connecting_prompt
    #     print("img_prompt:",img_prompt)
    #     genNum += 1
    #     output_path = gen_path + "generatedImg" + str(genNum) + '.png'
    #     img_path,img_URL = expand_image(img_path,scale_factor,img_prompt,output_path)
    bridge_img_1_path = output_path
    # condense from end image
    genNum = num_keyframes
    output_path = gen_path + "generatedImg" + str(genNum) + '.png'
    prev_path = output_path
    new_percent = 1/scale_factor
    img_path,img_URL = expand_image(end_img_path,1.0,img_prompt,output_path)
    # gen_img,img_URL = fill_center_of_image(end_img_path,new_percent,0.3,img_prompt,output_path)
    prev_percent = new_percent
    # genNum -= 1
    # output_path = gen_path + "generatedImg" + str(genNum) + '.png'
    # gen_img.save(output_path,"PNG")
    for i in range(num_outframes-1):
        if (i >= 0):
            img_prompt = connecting_prompt
            new_percent = 1/scale_factor
        print("img_prompt:",img_prompt)
        gen_img,img_URL = fill_center_of_image(output_path,new_percent,0.3,img_prompt,output_path)
        prev_img = Image.open(prev_path)
        w,h = prev_img.size
        prev_img = prev_img.resize((int((1/prev_percent)*w),int((1/prev_percent)*h)))
        w,h = prev_img.size
        prev_img.paste(gen_img,((w-gen_img.size[0])//2,(h-gen_img.size[1])//2))
        prev_img = prev_img.resize((int(prev_percent*w),int(prev_percent*h)))
        prev_img.save(prev_path,"PNG")
        prev_percent = new_percent
        prev_path = output_path
        genNum -= 1
        output_path = gen_path + "generatedImg" + str(genNum) + '.png'
        gen_img.save(output_path,"PNG")
        # input_path = output_path
        # gen_img,img_URL = fill_center_of_image(output_path,1/scale_factor,0.3,img_prompt,output_path)
        
    bridge_img_2_path = output_path
    # gen_img,img_URL = fill_center_of_image(img_path,0.1,0.3,img_prompt,output_path)
    bridge_the_gap(bridge_img_1_path,bridge_img_2_path,scale_factor,gen_path+"generatedImgB.png")



PARENT_PATH = "Infinite_Zoom/"
INPUT_PATH = PARENT_PATH + "input/"
SESSIONS_PATH = PARENT_PATH + "sessions/"
TEMP_PATH = PARENT_PATH + "temp/"

START_IMG = "city2.jpg"
END_IMG = "colby.jpg"
START_IMG_PATH = INPUT_PATH + START_IMG
END_IMG_PATH = INPUT_PATH + END_IMG

# img_URL,img_description = input_description_dict[START_IMG]
# start_URL,start_description = input_description_dict[START_IMG]
# end_URL,end_description = input_description_dict[END_IMG]
# rename_session_folders()
sessionNum = len(os.listdir(SESSIONS_PATH))
session_path = SESSIONS_PATH + "session" + str(sessionNum) + "/"
gen_path = session_path + "generations/"
out_path = session_path + "output/"

img_path = START_IMG_PATH
scale_factor = 1.5
num_keyframes = 20
img_prompt = "unidentifiable objects"
generate_transition_keyframes(START_IMG_PATH,END_IMG_PATH,num_keyframes,scale_factor)
# bridge_the_gap("Infinite_Zoom/sessions/session73/generations/generatedImg2.png","Infinite_Zoom/sessions/session73/generations/generatedImg3.png",scale_factor,"Infinite_Zoom/sessions/session73/generations/generatedImgB.png")

example_session = get_session_path(45)
example_keyframe_path_1 = example_session + "generations/generatedImg0.png"
example_keyframe_path_2 = example_session + "generations/generatedImg1.png"
# example_keyframes = generate_keyframe_transition_frames(4,example_keyframe_path_1,example_keyframe_path_2)
# generate_video_frames(24,10,"Infinite_Zoom/sessions/session12/generations/")
# generate_video_frames(120,30,"Infinite_Zoom/sessions/session45/generations/")

# delete all pre-existing frames
# for n in range(sessionNum):
#     cur_session = get_session_path(n)
#     delete_all_frames(cur_session+"output/")

frame_session = get_session_path(70)
keyframe_path = frame_session + "generations/"
frame_out_path = frame_session + "output/frames/"
video_out_path = frame_session + "output/"
fps = 24
video_duration = 5
# generate_video_frames(fps,video_duration,keyframe_path,frame_out_path)
# make_video_from_frames((1024,1024),fps,frame_out_path,frame_out_path)
# make_mp4_video_from_frames(fps,frame_out_path,video_out_path)
# delete_all_frames(frame_out_path)
# print(os.listdir(get_session_path(69)))

