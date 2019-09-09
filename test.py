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
import nltk.data
from nltk import tokenize

import numpy as np
from moviepy.editor import *

post_list = []
selected_list = []
text_list = []
headers = {'User-Agent': 'Mozilla/5.0'}
post_url = "https://www.reddit.com/r/{}.json"
language = 'en'

# RESOLUTION

w = 720
h = int(w*9/16) # 16/9 screen
moviesize = w,h

start_video_file = None
end_video_file = None
dir_name = "my_video"
dir_path = "."

def case1():
    return re.compile("\,")

# Tokenize the text for gtts        
def tokenize_text_with_audio(text):
    if not text or text == '\n':
        txt_clip = TextClip(text, fontsize = 10, color = 'white', method='label').set_duration(1)
        return txt_clip
    else:
        t = Tokenizer([case1])
        tokenized_text = t.run(text)
        audio_clip_list = []
        duration = 0
        for txt in tokenized_text:
            audioclip = generate_mp3(txt)
            audio_clip_list.append(audioclip.set_start(duration))
            duration += audioclip.duration
        
        compo = CompositeAudioClip(audio_clip_list)
        txt_clip = TextClip(text, align='West', fontsize = 25, color = 'white', method='caption', size=moviesize).set_duration(compo.duration).set_audio(compo)
        return txt_clip

def generate_mp3(text):
    myobj = gTTS(text=text, lang=language, slow=False) 
    myobj.save("text.mp3")
    return AudioFileClip("text.mp3")
 
def create_video():
    print('/------- creating video... ---------/\n')
    video_clips = []
    pdb.set_trace()
    # if Path(start_video_file).is_file():
    #     video_clips.append(CompositeVideoClip([VideoFileClip(start_video_file)]))
    for idx, text in enumerate(text_list):
        print(str(idx+1) + 'st text processing')
        if idx == 1:
            break
        try:
            video_clips.append(CompositeVideoClip([tokenize_text_with_audio(text)]))
        except UnicodeEncodeError:
            txt_clip = TextClip("Issue with text", fontsize = 70, color = 'white').set_duration(2) 
            video_clips.append(CompositeVideoClip([txt_clip]))

    # if Path(end_video_file).is_file():
    #     video_clips.append(CompositeVideoClip([VideoFileClip(end_video_file)]))
    
    concatenate_videoclips(video_clips, method='compose').write_videofile('{}/{}.mp4'.format(dir_path, dir_name), fps = 24, codec = 'mpeg4')
    
def tokenize_list(text):
    result_list= []
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    tokenized_list = tokenizer.tokenize(text)
    # tokenized_list = re.sub(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', '\n', text)
    
    length = 0
    result_text = ''
    for txt in tokenized_list:
        length += len(txt)
        if length < 300:
            result_text += txt + ' '
        else:
            result_list.append(result_text)
            result_text = ''
    
    return result_list
    
def adjust_length_of_text():
    new_list = []
    global text_list
    for text in text_list:
        text = re.sub(r"[,@\s+\*\\\\$%_]", " ", text, flags=re.I)
        if len(text) < 300:
            new_list.append(text)
        else:
            new_list = list(set(new_list + tokenize_list(text)))
    
    text_list = new_list
    
if __name__ == "__main__":
    print('---test---')
    text_list.append(
        'Well on about day 3 I\'m walking from the field to the class and see one of my students, 2nd grader, walking the other direction and ask him off-hand "How\'s chess going?  I\'ve lost all of my games so I guess I\'m doing great!"That\'s true in a lot of games, one thing that separates an average" Usually, at least with my friends, i have the basic understanding that if either of us has extra time or wants to chill, we ask but we don\'t put the pressure of a full on plan on it. Like i will ve in town anf ask if my friend has time, and if they don\'t, that\'s cool, i head home, if they do, that\'s great, we hang out. Well you arent wrong there buddy. I am currently going through a certain state this year. Seeing therapy and all. Depression and anxiety. Its more anxiety than anything. I am able to enjoy things still but anxiety gets me the most. And while they might not have those reactions, I know for a fact Im no one\'s first choice to talk to or hangout with (i know because Ive literally been indirectly told by them with comments like "oh yeah I was able to hangout today cuz \_\_\_\_\_\_ was busy"). I only have like 2-3 close friends. I have one person whom I refer to as a bestfriend, but I know they dont feel/think of me the same way because they are often talking about wishing they were with their bestfriend.'
    )
    
    adjust_length_of_text()
    create_video()