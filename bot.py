import json

from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters


updater = Updater("5788908830:AAGew0qIRF3l3TxR57Lcf4egiwbBU1XuBdo",
                  use_context=True)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
            "Hello sir, Welcome to the Bot.Please write\
		/help to see the commands available.")


def help(update: Update, context: CallbackContext):
    update.message.reply_text("""Available Commands :-
    /crypto - To show your crypto 
    
    """)


def crypto(update: Update, context: CallbackContext):
    with open("database.json") as f:
        data = json.load(f)
        update.message.reply_text(
            "Your crypto profile isn't set up, do you wish to set it up right now ?Y/N")
        print(update.message.from_user.id)


def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('crypto', crypto))

updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
updater.dispatcher.add_handler(MessageHandler(
    Filters.command, unknown))  # Filters out unknown commands

# Filters out unknown messages.
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

if __name__ == "__main__":
    updater.start_polling()
