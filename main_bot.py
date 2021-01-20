#!/usr/bin/env python3

import requests
import time
import argparse
import os
from os import path
import json
from utils import *
from dialogue_manager import DialogueManager
import spacy
import random
from requests.compat import urljoin
import emoji
import re
import voice_recognition

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)



with open("data/campus_answers.txt","r",encoding="utf-8") as f:
        answers= f.read().split('\n')
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
        elif question == "/random":
            return random.choice(answers)
        """elif question.lower()=="what is pmc" or question.lower()== "what is pmc?":
            return "Photography and Moviemaking Club (PMC) is the official photography and videography club of IIT Mandi. It is one of the most prominent and influential clubs of the cultural society. It conducts several events, workshops and sessions all year round. It has brought numerous laurels to the institute. For more info visit https://wiki.iitmandi.co.in/p/Photography_and_Moviemaking_Club"
        """
        reply=self.dialogue_manager.generate_answer(question)
        print(reply)
        return reply

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', type=str, default='')
    return parser.parse_args()


def is_unicode(text):
    return len(text) == len(text.encode("utf-8"))


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
                    text=text.encode('ascii', 'ignore').decode('ascii')
                    if is_unicode(text):
                        print("Update content: {}".format(update))
                        bot.send_message(chat_id, bot.get_answer(text))
                    else:
                        bot.send_message(chat_id, "Hmm, you are sending some weird characters to me...")
                if "voice" in update["message"]:
                    file_id=update["message"]["voice"]["file_id"]
                    text=voice_recognition.get(update["message"],token)
                    print(f"Did u said '{text}'")
                    bot.send_message(chat_id, f"Did u said '{text}'")
                    print("Update content: {}".format(update))
                    bot.send_message(chat_id, bot.get_answer(text))
            
            offset = max(offset, update['update_id'] + 1)
        time.sleep(1)

if __name__ == "__main__":
    main()
 