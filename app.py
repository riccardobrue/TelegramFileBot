import requests
import urllib
from urllib.request import urlopen
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

# ==============================================================================================
# Receives a file from the chat
# ==============================================================================================
def send_file(bot, update):
    chat_id = update.message.chat_id
    userInfo = update.message.from_user

    user_first_name = userInfo.first_name
    user_second_name = userInfo.last_name
    user_id = userInfo.id
    username = userInfo.username

    print("==================================")
    print("Chat ID: " + str(chat_id))
    print("User First Name: " + user_first_name)
    print("User Second Name: " + user_second_name)
    print("Username: " + username)
    print("User ID: " + str(user_id))
    print("==================================")

    file_name = update.message.document.file_name
    file_type = update.message.document.mime_type
    file_size = update.message.document.file_size

    print(file_name + "_" + str(file_type) + "_" + str(file_size))

    chat_file = bot.get_file(update.message.document.file_id)

    # ================================================================
    # Send a file to BlueCLoud website
    # ================================================================

    url = 'http://riccardobruetesting.altervista.org/APIs/file/file_api.php'

    file_temp_pathname, headers = urllib.request.urlretrieve(chat_file["file_path"])
    file = open(file_temp_pathname, 'rb')
    files = {'file': (file_name, file)}

    r = requests.post(url, files=files)
    print("Uploaded file result: " + r.text)

    # ================================================================
    update.message.reply_text("File received!")

# ==============================================================================================
# ==============================================================================================

def openshiftStart():
    updater = Updater('521661539:AAHoy9AKdBccWEwsgNWKoZpAlJc33UuzROE')
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.document, send_file))
    updater.start_polling()
    updater.idle()

openshiftStart()
