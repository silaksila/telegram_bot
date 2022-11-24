import logging
from functools import partial
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode
from bot_package.menu_filter import Menu_Filter
from bot_package.predict_lung_cancer import Predict_lung_cancer
from bot_package.crypto import reload_database, save_to_database, Crypto

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
token = "5788908830:AAGew0qIRF3l3TxR57Lcf4egiwbBU1XuBdo"

# TODO create reload func for database
# TODO create unique id for every user in database

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, crypto: Crypto):
    # TODO change when the load function is called
    crypto.load_job(update, context)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Hello, please type /help to show all commands")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="*Commands:* ", parse_mode=ParseMode.MARKDOWN_V2)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="/crypto - show your crypto profile \n"
                                        "/lungcancer - take quick quiz to predict how likely you are to get "
                                        "lung cancer in future\n/menu - go back to the menu")


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _, data = reload_database()
    save_to_database(0, data)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Main menu\nTo show commands type /help")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Unknown command, type /help to show all commands")

def main():
    menu_state, data = reload_database()
    crypto = Crypto(menu_state, data)
    lung_cancer = Predict_lung_cancer(menu_state)
    application = ApplicationBuilder().token(token).build()
    application.add_handler(MessageHandler(
        Menu_Filter(command="/start", menu_state=menu_state), partial(start, crypto=crypto)))
    application.add_handler(MessageHandler(
        Menu_Filter(command="/crypto", menu_state=menu_state), crypto.crypto))
    application.add_handler(MessageHandler(
        Menu_Filter(command="/help", menu_state=menu_state), help))
    application.add_handler(MessageHandler(
        Menu_Filter(command="/menu", menu_state=menu_state), menu))

    application.add_handler(MessageHandler(
        filters.MessageFilter(), unknown_command))
    application.add_handler(crypto.create_crypto_conversation())
    application.add_handler(lung_cancer.create_conversation_handler())

    application.run_polling()


if __name__ == '__main__':
    main()
