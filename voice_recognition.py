import telebot
import requests
import os 
from os import path
import subprocess
import json 
from os.path import join, dirname 
from ibm_watson import SpeechToTextV1 
from ibm_watson.websocket import RecognizeCallback, AudioSource 
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator 

def get(message,token):
    chat_id=message["chat"]["id"]
    bot = telebot.TeleBot(token)
    file_id=message["voice"]["file_id"]
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(f'audio/{file_id}.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)

    audiofile= path.join(path.dirname(path.realpath(__file__)), f"audio\\{file_id}.wav")

    src_filename = f"audio/{file_id}.ogg"
    dest_filename = f"audio/{file_id}.wav"

    process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])
    if process.returncode != 0:
        raise Exception("Something went wrong")
    print(audiofile)
    os.remove(src_filename)
  
    authenticator = IAMAuthenticator('ADD YOUR API KEY HERE')  
    service = SpeechToTextV1(authenticator = authenticator) 

    service.set_service_url('ADD YOUR API URL HERE') 

    with open((audiofile),'rb') as audio_file: 
        
            dic = json.loads( 
                    json.dumps( 
                        service.recognize( 
                            audio=audio_file, 
                            content_type='audio/wav',    
                            model='en-US_NarrowbandModel', 
                        continuous=True).get_result(), indent=2)) 
    
    str = "" 
    
    while bool(dic.get('results')): 
        str= dic.get('results').pop().get('alternatives').pop().get('transcript')+str[:]   
    os.remove(audiofile)
    return str

