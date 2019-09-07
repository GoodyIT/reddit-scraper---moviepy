#! usr/bin/env python3
import requests
import csv
import time
import json
import pdb
from gtts import gTTS 
from gtts.tokenizer.core import *
import os 
import re
from pathlib import Path

import numpy as np
from skimage import transform as tf

from moviepy.editor import *
from moviepy.video.tools.segmenting import findObjects
from moviepy.video.tools.drawing import color_gradient

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"/usr/bin/convert"})

post_list = []
selected_list = []
text_list = []
headers = {'User-Agent': 'Mozilla/5.0'}
post_url = "https://www.reddit.com/r/AskReddit.json"
language = 'en'

# RESOLUTION

w = 720
h = int(w*9/16) # 16/9 screen
moviesize = w,h

def case1():
    return re.compile("\,")

# def case2():
#     return RegexBuilder('abc', lambda x: "{}\.".format(x)).regex

def get_page():
    # Headers to mimic a browser visit

    print(' --- Running the scraper ---')
    # Returns a requests.models.Response object
    response = requests.get(post_url, headers=headers)
    if response.status_code == 200:
        result = json.loads(response.content)
    
        for idx, post in enumerate(result['data']['children']):
            post_list.append({
                "idx": str(idx+1),
                "id": post['data']['id'],
                "title": post['data']['title']
            })
            print('{}. {}'.format(idx, post['data']['title']))

def get_replies(_comment):
    try:
        text_list.append(_comment['body'])      
        if _comment['replies'] and len(_comment['replies']['data']['children']):
            for idx, reply in enumerate(_comment['replies']['data']['children']):
                print('---- '+ str(idx+1) +' reply----')
                get_replies(reply['data'])
            text_list.append('\n')
    except:
        pass
    
def get_comments():
    print('---- start getting the post----')
    for post in selected_list:
        print('---- '+ post['idx'] +' post----')
        text_list.append(post['title'])
        comment_url = 'https://www.reddit.com/r/AskReddit/comments/{}.json'.format(post['id'])
        response = requests.get(comment_url, headers=headers)
        if response.status_code == 200:
            comments = json.loads(response.content)
            for idx, comment in enumerate(comments[1]['data']['children']):
                print('---- '+ str(idx+1) +' comment----')
                text_list.append('\n')
                if comment['kind'] != 'more':
                    get_replies(comment['data'])
    
# Tokenize the text for gtts        
def tokenize_text_with_audio(text):
    if text == '\n':
        txt_clip = TextClip(text, fontsize = 10, color = 'white', method='label').set_duration(1)
        return txt_clip
    else:
        t = Tokenizer([case1])
        tokenized_text = t.run(text)
        txt_clip_list = []
        for txt in tokenized_text:
            audioclip = generate_mp3(txt)
            txt_clip = TextClip(txt, align='West', fontsize = 25, color = 'white', method='caption', size=moviesize).set_duration(audioclip.duration).set_audio(audioclip)
            txt_clip_list.append(txt_clip)
            
        return concatenate(txt_clip_list, method = "compose")

def generate_mp3(text):
    myobj = gTTS(text=text, lang=language, slow=False) 
    myobj.save("text.mp3")
    return AudioFileClip("text.mp3")
 
def create_video():
    clip_list = []

    print('/------- creating video... ---------/\n')
    # txt = "".join(text_list)
    video_clips = []
    if Path("./start.mp4").is_file():
        video_clips.append(CompositeVideoClip([VideoFileClip("./start.mp4")]))
    for idx, text in enumerate(text_list):
        print(str(idx+1) + 'st text processing')
        if idx == 1:
            break
        try:
            video_clips.append(CompositeVideoClip([tokenize_text_with_audio(text)]))
        except UnicodeEncodeError:
            txt_clip = TextClip("Issue with text", fontsize = 70, color = 'white').set_duration(2) 
            video_clips.append(CompositeVideoClip([txt_clip]))

    if Path("./end.mp4").is_file():
        video_clips.append(CompositeVideoClip([VideoFileClip("./end.mp4")]))
    
    concatenate_videoclips(video_clips, method='compose').write_videofile("my_video.mp4", fps = 24, codec = 'mpeg4')
    
def close_clip(clip):
    try:
        clip.reader.close()
        if clip.audio != None:
            clip.audio.reader.close_proc()
            del clip.audio
            del clip
    except Exception as e:
        print("Error in close_clip() ", e)
    
if __name__ == "__main__":
    print('waiting...')
    # create_video()
    get_page()
    is_run = False
    while True:
        choice = str(input("Scrape posts: 1. all(a) - All Posts, 2. input the post number with comma, 3. n - cancel\n"))
        if choice.lower() == 'all' or choice.lower() == 'a':
            is_run = True
            selected_list = post_list
            break
        elif choice.lower() == 'n':
            print("Cancel.")
            break
        else:
            idxs = choice.split(',')
            is_run = True
            for post in post_list:
                if post['idx'] in idxs:
                    selected_list.append(post)
            break
    
    if is_run:
        get_comments()
        
        f= open("data.txt","w+")
        f.writelines(text_list)
        
        create_video()
            
        