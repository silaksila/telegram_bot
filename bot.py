import logging
from functools import partial
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode
from bot_package.menufilter import MenuFilter
from bot_package.predictlungcancer import PredictLungCancer
from bot_package.crypto import reload_database, Crypto

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
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
                                   text=f"/crypto - show your crypto profile \n"
                                        "/lungcancer - take quick quiz to predict how likely you are to get lung cancer"
                                f"in future\n/menu - go back to the menu\n/sudoku - solve sudoku")


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Main menu\nTo show commands type /help")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Unknown command, type /help to show all commands")


def main():
    token = "5788908830:AAGew0qIRF3l3TxR57Lcf4egiwbBU1XuBdo"
    menu_state, data = reload_database()
    crypto = Crypto(menu_state, data)
    lung_cancer = PredictLungCancer(menu_state)
    application = ApplicationBuilder().token(token).build()
    application.add_handler(MessageHandler(
        MenuFilter(command="/start"), partial(start, crypto=crypto)))
    application.add_handler(MessageHandler(
        MenuFilter(command="/crypto"), crypto.crypto))
    application.add_handler(MessageHandler(
        filters.Regex("help"), help))
    application.add_handler(MessageHandler(
        MenuFilter(command="/menu"), menu))

    application.add_handler(MessageHandler(
        filters.MessageFilter(), unknown_command))
    application.add_handler(crypto.create_crypto_conversation())
    application.add_handler(lung_cancer.create_conversation_handler())

    application.run_polling()


if __name__ == '__main__':
    main()
