#! usr/bin/env python3
import requests
import csv
import time
import json
import pdb
from gtts import gTTS 
import os 

import numpy as np
from moviepy.editor import *
from moviepy.video.tools.segmenting import findObjects

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"/usr/bin/convert"})

post_list = []
selected_list = []
text_list = []
headers = {'User-Agent': 'Mozilla/5.0'}
post_url = "https://www.reddit.com/r/AskReddit.json"
language = 'en'

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
    
    for text in text_list:
        pdb.set_trace()
        myobj = gTTS(text=text, lang=language, slow=False) 
        myobj.save("welcome.mp3") 
        os.system("mpg321 welcome.mp3") 
        # time.delay(3)
    
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
    
def create_video():
    clip_list = []

    for post in selected_list:
        text = post['title']
        try:
            txt_clip = TextClip(text, fontsize = 70, color = 'white').set_duration(2)
            clip_list.append(txt_clip)
        except UnicodeEncodeError:
            txt_clip = TextClip("Issue with text", fontsize = 70, color = 'white').set_duration(2) 
            clip_list.append(txt_clip)

    final_clip = concatenate(clip_list, method = "compose")
    final_clip.write_videofile("my_concatenation.mp4", fps = 24, codec = 'mpeg4')

if __name__ == "__main__":
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
        # get_comments()
        create_video()
        