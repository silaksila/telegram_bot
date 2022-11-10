import json

from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters


updater = Updater("5788908830:AAGew0qIRF3l3TxR57Lcf4egiwbBU1XuBdo",
                  use_context=True)
user_id = "5052059958"

with open("database.json") as f:
    data = json.load(f)


def get_state(str_id):
    """state meaning:
    0- main menu(nothing has been selected
    1- in crypto menu
    2- about to create a crypto profile
    #TODO
    """
    return data[str_id]["state"]


def start(update: Update, context: CallbackContext):
    global user_id
    user_id = str(update.message.from_user.id)
    if user_id not in data:
        # TODO add new user
        print("add new user")
    update.message.reply_text(
            "Hello sir, Welcome to the Bot.Please write\
		/help to see the commands available.")


def help(update: Update, context: CallbackContext):
    update.message.reply_text("""Available Commands :-
    /crypto - To show your crypto 
    
    """)


def command(update: Update, context: CallbackContext):
    commands = ['/start', '/help', '/crypto']
    txt = update.message.text
    print(txt)
    if txt in commands:
        txt = commands.index(txt)
        if get_state(user_id) == 0:
            if txt == 0:
                start()
            elif txt == 1:
                help()
            else:
                crypto()

    else:
        update.message.reply_text(
            "Sorry '%s' is not a valid command" % update.message.text)


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)


def crypto(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Your crypto profile isn't set up, do you wish to set it up right now ?Y/N")
    print(update.message.from_user.id)


#updater.dispatcher.add_handler(CommandHandler('start', start))
#updater.dispatcher.add_handler(CommandHandler('help', help))
#updater.dispatcher.add_handler(CommandHandler('crypto', crypto))

updater.dispatcher.add_handler(MessageHandler(
    Filters.command, command))  # Filters out unknown commands

# Filters out unknown messages.
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))


if __name__ == "__main__":
    updater.start_polling()
    updater.idle()
