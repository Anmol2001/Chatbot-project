import telebot
def get(message,token,chat_id):
    bot = telebot.TeleBot(token)
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    return downloaded_file