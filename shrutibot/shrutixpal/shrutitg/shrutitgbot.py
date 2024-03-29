# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
# from shrutitgbot.xpal import *
# SHRUTI - This is a class of bots that Mojolab, Hackergram and other linked entities use for the purpose of comprehension and gateway building
from . import xpal
from . import utils
import requests, json

# from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
#                          ConversationHandler)
from telegram.ext import (CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler, CallbackContext)
from telegram import ReplyKeyboardMarkup, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update, ReplyKeyboardRemove
import xetrapal
from xetrapal import telegramastras
import os
verbose=False
#vocal=True
#import sys

#sys.path.append("/opt/xetrapal")

# FEATURE LIST
# TODO: #7 FEATURE - Add a function to handle replies to messages

#TODO: #5 #4 fix hardcoded path to better approch
memberbotconfig = xetrapal.karma.load_config(configfile="/opt/shrutibot-appdata/shrutitgbot.conf")
shrutitgbot=xetrapal.telegramastras.XetrapalTelegramBot(config=memberbotconfig, logger=xpal.shrutitgbotxpal.logger)
logger = shrutitgbot.logger
GETMOBILE, PROCESS_MESSAGE = range(2)

send_contact_text = u'\U0001F4CD Send Contact'

loop_text = u'\U0001F960 Loop'
exit_text = u'\U0001F44B Bye'
#contact_keyboard = [
#                    [{'text': send_contact_text, 'request_contact': True}]
#                    ]
#member_base_keyboard = [
#                        [exit_text]
#                        ]

main_menu_header_text = '''\

Hi! My name is Shruti.
If you send me an audio prompt, I will convert it to text using the <a href='https://cloud.google.com/speech-to-text'>Google Speech API</a> and then use the <a href='https://beta.openai.com/examples/default-marv-sarcastic-chat'> OpenAI GPT example of Marv the sarcastic chatbot</a> to respond
I also speak GOAT

'''

# Create a triple
def facts_to_str(user_data):
    facts = list()
    logger.info("Converting facts to string")
    for key, value in user_data.items():
        facts.append(u'{} - {}'.format(key, repr(value)))
    logger.info("Converted facts to string")
    return "\n".join(facts).join(['\n', '\n'])

def get_audio(text,path):
    command='espeak -w {} -v en-us "{}"'.format(os.path.join(path,"respfile.wav"),text)
    os.system(command)
    return os.path.join(path,"respfile.wav")

# Send a message to and get a response from the locally running Shruti API
def get_shruti_response(username,message,hostname="http://localhost"):
    resturl=":5000/listener"
    jsondata={}
    jsondata['sender']=username
    jsondata['text']=message.text
    jsondata['media']=None
    jsondata['source']="telegram"
    if "reply_to_message" in message.to_dict().keys():
        jsondata['reply_to_message']=message.reply_to_message.to_dict()
    if message.photo or message.document or message.voice or message.audio:
        logger.info("Media found")
        media=get_media(message)
        logger.info("Media path {}".format(media))
        jsondata['media']=media
    logger.info("Trying",jsondata)

    response=requests.post(hostname+resturl,json=jsondata)
    return response.json()

# Function to present the main menu
def main_menu(update: Update, context: CallbackContext):
    logger.info(context.user_data)
    user_data = context.user_data
    try:
        #user_data['member'] = xpal.get_member_by_tgid(update.message.from_user.id)
        user_data['member'] = xpal.get_member_by_username(update.message.from_user.username)
        logger.info(u"{}".format(user_data))
        if user_data['member'] is None:
            update.message.reply_text("Sorry, this service is for whitelisted members only.")
            #return ConversationHandler.END
            return GETMOBILE
        logger.info("Main Menu presented to member {}".format(user_data['member'].username))
        update.message.reply_text(main_menu_header_text,  parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
        return PROCESS_MESSAGE
    except Exception as e:
        logger.error("{} {}".format(type(e), str(e)))


# Function to download and return path to media if telegram.Message object contains media
def get_media(message):
    media={}
    if message.photo:
        media_id = message.photo[-1]
        # generate file name from message.from_user.id and media_id
        filename = '{}_{}.jpg'.format(message.from_user.username, media_id.file_unique_id)
        media_id.get_file().download(custom_path=os.path.join(xpal.shrutitgbotxpal.sessionpath, filename))
        media['type']='photo'
        media['path']=os.path.join(xpal.shrutitgbotxpal.sessionpath, filename)
    if message.document:
        media_id = message.document 
        # generate file name from message.from_user.id and media_id
        filename = '{}_{}'.format(message.from_user.username, media_id.file_name)
        media_id.get_file().download(custom_path=os.path.join(xpal.shrutitgbotxpal.sessionpath, filename))
        media['type']='document'
        media['path']=os.path.join(xpal.shrutitgbotxpal.sessionpath, filename)
    if message.voice:
        media_id = message.voice
        # generate file name from message.from_user.id and media_id
        filename = '{}_{}.ogg'.format(message.from_user.username, media_id.file_unique_id)
        media_id.get_file().download(custom_path=os.path.join(xpal.shrutitgbotxpal.sessionpath, filename))
        media['type']='voice'
        media['path']=os.path.join(xpal.shrutitgbotxpal.sessionpath, filename)
    if message.audio:
        media_id = message.audio
        # generate file name from message.from_user.id and media_id
        filename = '{}_{}'.format(message.from_user.username, media_id.file_name)
        media_id.get_file().download(custom_path=os.path.join(xpal.shrutitgbotxpal.sessionpath, filename))
        media['type']='audio'
        media['path']=os.path.join(xpal.shrutitgbotxpal.sessionpath, filename)
    return media


def loop(update: Update, context: CallbackContext):
    if update.message.text=="/bye":
        return exit(update,context)
    logger.info("Received from: {} message: {}".format(context.user_data['member'].username,update.message))   
    message=get_shruti_response(username=context.user_data['member'].username, message=update.message)
    response=message['response']
    logger.info("Response: {}".format(response))
    if verbose:
        try:
            update.message.reply_text(str(message), parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
        except Exception as e:
            update.message.reply_text("Error: {}".format(str(e)), parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
    
    if type(response)==list:
        if len(response)>50:
            response=response[:50]
        if '' in response:
            response.remove('')
        if len(response)>0:
            for line in response:
                update.message.reply_text(line, parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
        else:
            update.message.reply_text("No response", parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
    if type(response)==dict:
        if 'text' not in response.keys() and 'media' not in response.keys():
            logger.info("Not a text response or media file")
            update.message.reply_text(json.dumps(response,ensure_ascii=False), parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
        if 'media' in response.keys() and response['media']['type']=='audio':
            update.message.reply_audio(audio=open(response['media']['path'],'rb'), parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
        if 'text' in response.keys():
            update.message.reply_text(response['text'], parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
       
    if type(response)==str:
        update.message.reply_text(response, parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
    return PROCESS_MESSAGE

def set_mobile(update: Update, context: CallbackContext):
    logger.info(u"{}".format(update.message.contact))
    member = xpal.get_member_by_mobile(update.message.contact.phone_number.lstrip("+"))
    if member:
        member.tgid = update.message.contact.user_id
        member.save()
        user_data['member'] = member
        logger.info("Main Menu presented to member {}".format(user_data['member'].username))
        markup = ReplyKeyboardMarkup(member_base_keyboard, one_time_keyboard=True)
        update.message.reply_text(main_menu_header_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        return PROCESS_MESSAGE
    else:
        update.message.reply_text("Sorry, you don't seem to be listed!")
        return ConversationHandler.END


def cancel(bot, update, user_data):
    logger.info(u"Cancelling Update {}".format(user_data))
    markup = ReplyKeyboardMarkup(member_base_keyboard, one_time_keyboard=True)
    update.message.reply_text(u'Cancelled!', reply_markup=markup)
    return PROCESS_MESSAGE


def exit(update: Update, context: CallbackContext):
    update.message.reply_text("Bye!")
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


states={
    GETMOBILE: [MessageHandler(Filters.text,
                               exit,
                               pass_user_data=True),
                MessageHandler(Filters.contact,
                               set_mobile,
                               pass_user_data=True),
                ],
    PROCESS_MESSAGE: [
                    MessageHandler(Filters.update, loop, pass_user_data=True)
                  ],

}


def setup():
    # Create the Updater and pass it your bot's token.
    updater = shrutitgbot.updater
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', main_menu)],
        states=states,
        fallbacks=[]#[RegexHandler('^[dD]one$', exit, pass_user_data=True)]
    )
    dp.add_handler(conv_handler)
    # log all errors
    dp.add_error_handler(error)
    # Start the Bot
    # updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    # updater.idle()


def single_update():
    p = shrutitgbot.get_latest_updates()
    for update in p:
        shrutitgbot.updater.dispatcher.process_update(update)
    return p


if __name__ == '__main__':
    setup()
    shrutitgbot.updater.start_polling()
    shrutitgbot.updater.idle()
