import logging
import db_manager
import datetime
import requests
from urllib.request import urlopen
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

DATE, MESSAGE = range(2)


# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#post-an-image-file-from-disk
# http://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.updater.html?highlight=updater
# https://github.com/python-telegram-bot/python-telegram-bot#documentation

# ==============================================================================================
def help(bot, update):
    helpText = "Hello! this is the CountdownBot!\n" \
               "List of commands:\n" \
               "- /insert : Start the countdown inseriment process\n" \
               "-- /dismiss : Dismiss the current insertion process\n" \
               "-- /skip : Skip the inseriment of a 'message' for the countdown\n" \
               "- /show : Shows all the saved countdowns\n" \
               "- /remove_all : Removes all the saved countdowns\n" \
               "- /delete <index>: Removes the given countdown by the index\n" \
               "- /start <index> : Starts the selected countdown notifications\n" \
               "- /stop <index> : Stops the selected countdown notifications\n" \
               "- /get <index> : Shows how many days left in a countdown"
    update.message.reply_text(helpText)


# ==============================================================================================
# ==============================================================================================
def alarm(bot, job):
    """Send the alarm message."""
    bot.send_message(job.context, text='Beep!')


# ==========================------------------------------------
def start(bot, update, args, job_queue, chat_data):
    chat_id = update.message.chat_id
    userName = update.message.from_user.first_name

    if (args[0] != None and isinstance(int(args[0]), int)):
        index = int(args[0])
        countdown = db_manager.getSingle(chat_id, userName, index - 1)  # because starts from 1
        date = countdown["date"]
        message = countdown["message"]
        today = datetime.datetime.utcnow()

        notificationtime = "02:00"

        update.message.reply_text("DATE: " + str(date) + "\n" + "MESSAGE: " + message + "\n" + "TODAY: " + str(today))

        try:
            # args[0] should contain the time for the timer in seconds
            due = int(args[0])
            if due < 0:
                update.message.reply_text('Sorry we can not go back to future!')
                return

            # Add job to queue
            job = job_queue.run_once(alarm, due, context=chat_id)
            chat_data['job'] = job

            update.message.reply_text('Timer successfully set!')

        except (IndexError, ValueError):
            update.message.reply_text('Usage: /set <seconds>')

    else:
        update.message.reply_text("You must specify which countdown to start!")


# ==========================------------------------------------
def stop(bot, update, chat_data):
    """Remove the job if the user changed their mind."""
    if 'job' not in chat_data:
        update.message.reply_text('You have no active timer')
        return
    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']
    update.message.reply_text('Timer successfully unset!')


# ==============================================================================================
def instantGet(bot, update, args):
    chat_id = update.message.chat_id
    userName = update.message.from_user.first_name

    if (args[0] != None and isinstance(int(args[0]), int)):
        index = int(args[0])
        countdown = db_manager.getSingle(chat_id, userName, index - 1)  # because starts from 1

        targetDate = datetime.datetime.strptime(countdown["date"], '%d-%m-%Y').date()
        message = countdown["message"]
        today = datetime.datetime.utcnow().date()

        difference = targetDate - today

        update.message.reply_text(str(difference.days) + " days left!")

    else:
        update.message.reply_text("You must specify which countdown to show!")


# ==============================================================================================
# ==============================================================================================
# ==============================================================================================
# ==============================================================================================
def clear(user_data):
    if 'data' in user_data:
        del user_data['data']
    user_data.clear()


# ==========================------------------------------------
def timer_insert(bot, update):
    user = update.message.from_user
    logger.info("Start received from %s: %s", user.first_name, update.message.text)
    response = "Hello!\n" \
               "Instantiate a countdown\n" \
               "Please send me a date (dd-mm-yyyy)\n" \
               "[You can /dismiss this process]"
    update.message.reply_text(response)
    return DATE


# ==========================------------------------------------
def set_timer_date(bot, update, user_data):
    user = update.message.from_user
    logger.info("Countdown date from %s: %s", user.first_name, update.message.text)
    targetDate = datetime.datetime.strptime(update.message.text, '%d-%m-%Y').date()
    today = datetime.datetime.utcnow().date()

    if (today < targetDate):
        response = "Date stored!\n" \
                   "Send a message for this countdown\n" \
                   "or type /skip to terminate"
        update.message.reply_text(response)
        user_data['data'] = update.message.text
        return MESSAGE
    else:
        clear(user_data)
        update.message.reply_text('Date not valid!')
        return ConversationHandler.END


# ==========================------------------------------------
def set_timer_message(bot, update, user_data):
    set_countdown(bot, update, update.message.text, user_data['data'])
    clear(user_data)
    return ConversationHandler.END


# ==========================------------------------------------
def skip_timer_message(bot, update, user_data):
    set_countdown(bot, update, None, user_data['data'])
    clear(user_data)
    return ConversationHandler.END


# ==========================------------------------------------
def set_countdown(bot, update, message, data):
    db_manager.add(update.message.chat_id, update.message.from_user.first_name, message, data, 0)
    update.message.reply_text("Countdown set\n"
                              "Do not forget to /start <index> the countdown!\n"
                              "Bye!")


# ==========================------------------------------------
def dismiss(bot, update, user_data):
    user = update.message.from_user
    logger.info("User %s dismissed the conversation.", user.first_name)
    update.message.reply_text('Dismissed. Bye!')
    clear(user_data)
    return ConversationHandler.END


# ==============================================================================================
def show_countdowns(bot, update):
    user = update.message.from_user
    chat_id = update.message.chat_id
    logger.info("Message from %s: %s", user.first_name, update.message.text)

    countdowns = db_manager.getAll(chat_id, user.first_name)
    message = ""
    for countdown in countdowns:
        message += str(countdown["counter"] + 1) + ")" + str(countdown["date"]) + ": " + countdown["message"] + "\n"
    if (message == ""):
        message = "No countdowns to display!"
    update.message.reply_text(message)


# ==============================================================================================
def delete_single(bot, update, args):
    userName = update.message.from_user.first_name
    chat_id = update.message.chat_id

    if (args[0] != None and isinstance(int(args[0]), int)):
        index = int(args[0])
        result = db_manager.removeOne(chat_id, userName, index - 1)  # because starts from 1
        update.message.reply_text(result)
        return
    else:
        update.message.reply_text("You must specify the countdown to remove")


# ==========================------------------------------------
def delete_all(bot, update):
    userName = update.message.from_user.first_name
    chat_id = update.message.chat_id
    result = ""
    result = db_manager.removeAll(chat_id, userName)
    if (result == ""):
        result = "No countdowns to remove!"
    update.message.reply_text(result)


# ==============================================================================================
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


# ==============================================================================================


# ==============================================================================================
# ==============================================================================================
def get_image(bot, update):
    # userName = update.message.from_user.first_name
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo='https://telegram.org/img/t_logo.png')


# ==========================------------------------------------
def get_file(bot, update):
    # userName = update.message.from_user.first_name
    chat_id = update.message.chat_id
    # url = "https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/505218/IC_Energy_Report_web.pdf"
    url = "https://github.com/riccardobrue/hello_world/blob/master/testing_zip.zip?raw=true"
    file = urlopen(url)
    file.name = 'testing.zip'

    meta = file.info()
    byte_size = int(meta["Content-Length"])
    print("SIZE (bytes): " + str(byte_size))
    if byte_size >= 20000000:
        update.message.reply_text("File too large to be downloaded via telegram!")
    else:
        bot.send_document(chat_id=chat_id, document=file)
        # bot.send_document(chat_id=chat_id, document=open('tests/test.zip', 'rb'))


# ==============================================================================================
# Receives a file from the chat
# ==============================================================================================
def send_file(bot, update):
    chat_id = update.message.chat_id
    userInfo = update.message.from_user
    # userContact = update.message.contact

    user_first_name = userInfo.first_name
    user_second_name = userInfo.last_name
    # phone_number = userContact.phone_number
    user_id = userInfo.id
    username = userInfo.username

    print("==================================")
    print("Chat ID: " + str(chat_id))
    print("User First Name: " + user_first_name)
    print("User Second Name: " + user_second_name)
    print("Username: " + username)
    print("User ID: " + str(user_id))
    # print("Phone Number: " + phone_number)
    print("==================================")

    file_name = update.message.document.file_name
    file_type = update.message.document.mime_type
    file_size = update.message.document.file_size

    print(file_name + "_" + str(file_type) + "_" + str(file_size))

    chat_file = bot.get_file(update.message.document.file_id)
    file = urlopen(chat_file["file_path"])

    print("Type: "+type(file))
    print("File: "+file)
    # ================================================================
    # Trying to send a file to Altervista
    # ================================================================
    url = 'http://riccardobruetesting.altervista.org/APIs/file/file_api.php'
    r = requests.post(url, files={file_name: file})

    # ================================================================
    file.download('file.jpg')
    print("File of" + user_first_name + 'user_photo.jpg' + file_name + "." + file_type + " (" + str(file_size) + ")")

    update.message.reply_text("File received!")


# ==============================================================================================
# ==============================================================================================


def openshiftStart():
    updater = Updater('541177999:AAE3-K_4-pj7WMMLnjS4PPnG1NeHdMiqVa4')
    dispatcher = updater.dispatcher

    # ==============================================================================================
    # Add conversation handler with the states DATE and MESSAGE
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('insert', timer_insert)],
        states={
            DATE: [
                RegexHandler('^([0]?[1-9]|[1|2][0-9]|[3][0|1])[-]([0]?[1-9]|[1][0-2])[-]([0-9]{4}|[0-9]{2})$',
                             set_timer_date, pass_user_data=True)
            ],
            MESSAGE: [
                MessageHandler(Filters.text, set_timer_message, pass_user_data=True),
                RegexHandler('^([/]skip)$', skip_timer_message, pass_user_data=True)
            ]
        },
        fallbacks=[
            RegexHandler('^([/]dismiss)$', dismiss, pass_user_data=True)
        ]
    )
    dispatcher.add_handler(conv_handler)
    # ==============================================================================================
    """
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            GENDER: [RegexHandler('^(Boy|Girl|Other)$', gender)],

            PHOTO: [MessageHandler(Filters.photo, photo),
                    CommandHandler('skip', skip_photo)],

            LOCATION: [MessageHandler(Filters.location, location),
                       CommandHandler('skip', skip_location)],

            BIO: [MessageHandler(Filters.text, bio)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    """

    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('show', show_countdowns))
    dispatcher.add_handler(CommandHandler("delete", delete_single, pass_args=True))
    dispatcher.add_handler(CommandHandler('remove_all', delete_all))

    # test get image
    dispatcher.add_handler(CommandHandler('get_image', get_image))
    dispatcher.add_handler(CommandHandler('get_file', get_file))

    # dispatcher.add_handler(CommandHandler('send_file', send_file, pass_args=True))
    dispatcher.add_handler(MessageHandler(Filters.document, send_file))

    dispatcher.add_handler(CommandHandler("start", start,
                                          pass_args=True,
                                          pass_job_queue=True,
                                          pass_chat_data=True))

    dispatcher.add_handler(CommandHandler("stop", stop,
                                          pass_args=True,
                                          pass_chat_data=True))

    dispatcher.add_handler(CommandHandler("get", instantGet,
                                          pass_args=True))

    # log all errors
    dispatcher.add_error_handler(error)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    updater.start_polling()
    updater.idle()


def localTesting():
    message = db_manager.add(30, "test123", "testing message", "06/02/2018", 0)
    print(message)
    # message=db_manager.edit(30,"test123","test345","06/03/2019",0)
    # print(message)
    countdown = db_manager.getSingle(30, "test123", 0)
    # print(message)
    # record=db_manager.getAll(30,"test123")
    # for doc in record:
    #   print(doc)

    targetDate = datetime.datetime.strptime(countdown["date"], '%d/%m/%Y').date()
    message = countdown["message"]
    today = datetime.datetime.utcnow().date()

    difference = targetDate - today

    print("DATE: " + str(targetDate) + "\nMESSAGE: " + message + "\nTODAY: " + str(today) + "\nDIFFERENCE: ")

    print(str(difference.days))


openshiftStart()
# localTesting()

# localTesting()
# import test
# test.mainTest()


"""
You: /setprivacy

BotFather: Choose a bot to change group messages settings.

You: @your_name_bot

BotFather: 'Enable' - your bot will only receive messages that either start with the '/' symbol or mention the bot by username.

'Disable' - your bot will receive all messages that people send to groups.

Current status is: ENABLED

You: Disable

BotFather: Success! The new status is: DISABLED. /help

"""
