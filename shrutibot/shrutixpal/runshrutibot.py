# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from shrutitg.shrutitgbot import *


if __name__ == '__main__':
	setup()
	shrutitgbot.updater.start_polling()
	xpal.shrutitgbotxpal.logger.info("Bot is trying to poll for new messages")

	shrutitgbot.updater.idle()
