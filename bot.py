import json
import threading
import requests

from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

with open("database.json") as f:
    data = json.load(f)

updater = Updater("5788908830:AAGew0qIRF3l3TxR57Lcf4egiwbBU1XuBdo",
                  use_context=True)
key = key = "https://api.binance.com/api/v3/ticker/price?symbol="


menu = data["menu"]


def start(update: Update, context: CallbackContext):
    if menu == 0:
        update.message.reply_text(
                "Welcome to the Bot. Please write\
		    /help to see the commands available.")


def curr_menu():
    pass


def help(update: Update, context: CallbackContext):
    update.message.reply_text("""Available Commands :-
    /crypto - To show your crypto 
    
    """)


def crypto(update: Update, context: CallbackContext):
    if menu == 0:
        # get data from binance api nad from database,
        crypto = data["crypto"]["coins"]
        crypto_amounts = list(crypto.values())
        crypto_names = list(crypto.keys())
        curr = "BTCUSDT"
        url = key+curr
        price = requests.get(url)
        price = price.json()
        btc_price = float(price["price"])
        diff_from_old_price = ((btc_price/crypto_amounts[0][1])-1)*100
        if data["crypto"]["setup"]:
            update.message.reply_text(
                f"*bold*Current state: \n {crypto_names[0]} : {btc_price:,.2f} $  {diff_from_old_price:.2f} %".replace(",", " ").replace(".", ","))
            update.message.reply_text(
                f"Your crypto profile:\n {crypto_names[0]} : {crypto_amounts[0][0]*btc_price:.2f}. $ ".replace(".", ","))
        else:
            update.message.reply_text(
                "Your crypto profile isn't set up, do you wish to set it up right now ?Y/N")


def shutdown():
    updater.stop()
    updater.is_idle = False


def stop(bot, update):
    threading.Thread(target=shutdown).start()


def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help,))
updater.dispatcher.add_handler(CommandHandler('crypto', crypto))
updater.dispatcher.add_handler(CommandHandler('stop', stop))


updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
updater.dispatcher.add_handler(MessageHandler(
    Filters.command, unknown))  # Filters out unknown commands

# Filters out unknown messages.
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

if __name__ == "__main__":
    updater.start_polling()
