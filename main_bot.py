#!/usr/bin/env python3

import requests
import time
import argparse
import os
import json
from utils import *
from dialogue_manager import DialogueManager
import spacy
import random
from requests.compat import urljoin
import speech_recognition as sr
#import audiodownloader

r = sr.Recognizer()

with open("campus_answers.txt","r",encoding="utf-8") as f:
        answers= f.read().split('\n')
        answers= [re.sub(r"\[\w+\]",'hi',line) for line in answers]
        answers= [" ".join(re.findall(r"\w+",line)) for line in answers]
class BotHandler(object):
    """
        BotHandler is a class which implements all back-end of the bot.
        It has tree main functions:
            'get_updates' — checks for new messages
            'send_message' – posts new message to user
            'get_answer' — computes the most relevant on a user's question
    """

    def __init__(self, token, dialogue_manager):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
        self.dialogue_manager = dialogue_manager

    def get_updates(self, offset=None, timeout=30):
        params = {"timeout": timeout, "offset": offset}
        raw_resp = requests.get(urljoin(self.api_url, "getUpdates"), params)
        try:
            resp = raw_resp.json()
        except json.decoder.JSONDecodeError as e:
            print("Failed to parse response {}: {}.".format(raw_resp.content, e))
            return []

        if "result" not in resp:
            return []
        return resp["result"]

    def send_message(self, chat_id, text):
        params = {"chat_id": chat_id, "text": text}
        return requests.post(urljoin(self.api_url, "sendMessage"), params)

    def get_answer(self, question):
        if question == '/start':
            return "Hi there, How can I help you today?"
        elif question == "/random fact":
            return random.choice(answers)
        """elif question.lower()=="what is pmc" or question.lower()== "what is pmc?":
            return "Photography and Moviemaking Club (PMC) is the official photography and videography club of IIT Mandi. It is one of the most prominent and influential clubs of the cultural society. It conducts several events, workshops and sessions all year round. It has brought numerous laurels to the institute. For more info visit https://wiki.iitmandi.co.in/p/Photography_and_Moviemaking_Club"
        """
        reply21=self.dialogue_manager.generate_answer(question)
        print(reply21)
        return reply21

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', type=str, default='')
    return parser.parse_args()


def is_unicode(text):
    return len(text) == len(text.encode())


class SimpleDialogueManager(object):
    """
    This is the simplest dialogue manager to test the telegram bot.
    Your task is to create a more advanced one in dialogue_manager.py."
    """
    
    def generate_answer(self, question): 
        return "Hello, world!" 
        

def main():
    token = '1547700302:AAERs9g0D40N-VvW0TIh5jvJc1EujMjC8nc'

    if not token:
        if not "TELEGRAM_TOKEN" in os.environ:
            print("Please, set bot token through --token or TELEGRAM_TOKEN env variable")
            return
        token = os.environ["TELEGRAM_TOKEN"]

   
    # This is the point where you plug it into the Telegram bot. 
    # Do not forget to import all needed dependencies when you do so.
    
    dialogue_manager = DialogueManager(RESOURCE_PATH)
    dialogue_manager.create_chitchat_bot()
    bot = BotHandler(token, dialogue_manager)
   
    print("Ready to talk!")
    offset = 0
    while True:
        updates = bot.get_updates(offset=offset)
        for update in updates:
            print("An update received.")
            if "message" in update:
                chat_id = update["message"]["chat"]["id"]
                if "text" in update["message"]:
                    text = update["message"]["text"]
                    if is_unicode(text):
                        print("Update content: {}".format(update))
                        bot.send_message(chat_id, bot.get_answer(update["message"]["text"]))
                        
                    else:
                        bot.send_message(chat_id, "Hmm, you are sending some weird characters to me...")
            """
            if "message" in update:
                chat_id = update["message"]["chat"]["id"]
                flag=0
                if "voice" in update["message"]:
                    audio=audiodownloader.get(update["message"],token,chat_id)
                    audio=r.record(audio)
                    try:
                        text=r.recognize_sphinx(audio)
                        print(text)
                    except sr.UnknownValueError:
                        flag=1
                        bot.send_message("could not understand audio") 
                    if is_unicode(text) and flag==0:
                        print("Update content: {}".format(update))
                        bot.send_message(chat_id, bot.get_answer(text))
            """
            offset = max(offset, update['update_id'] + 1)
        time.sleep(1)

if __name__ == "__main__":
    main()
