import logging
import requests
import json
from telegram import Update, Message
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from telegram.constants import ParseMode

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
token = "5788908830:AAGew0qIRF3l3TxR57Lcf4egiwbBU1XuBdo"

with open("database.json") as f:
    data = json.load(f)

key = "https://api.binance.com/api/v3/ticker/price?symbol="


menu = data["menu"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Hello, please type /crypto to show your crypto")


async def stop(bot, update):
    await application.stop()


async def crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get data from database,
    crypto = data["crypto"]["coins"]
    crypto_amounts = list(crypto.values())
    crypto_names = list(crypto.keys())

    if data["crypto"]["setup"]:
        # get crypto price from binance api
        urls = [key+name+"USDT" for name in crypto_names]
        prices = [requests.get(url).json() for url in urls]

        crypto_profile_string = ""
        curr_state_string = ""
        for indx, val in enumerate(prices):
            crypto_price = float(val["price"])
            difference_to_old_price = (
                (crypto_price/crypto_amounts[indx][1])-1)*100
            curr_state_string += (
                f"{crypto_names[indx]} : {crypto_price:,.2f} $  {difference_to_old_price:+.2f} %\n")

            crypto_profile_string += (
                f"{crypto_names[indx]} : {crypto_amounts[indx][0]*crypto_price:.2f}. $ \n")
            data["crypto"]["coins"][crypto_names[indx]][1] = crypto_price

        with open("database.json", "w") as file:  # write new price values to later compare to
            json.dump(data, file)

        await context.bot.send_message(chat_id=update.effective_chat.id, text="*Current state:* \n", parse_mode=ParseMode.MARKDOWN_V2)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=curr_state_string.replace(",", " ").replace(".", ","))

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*Your crypto profile:*\n ", parse_mode=ParseMode.MARKDOWN_V2)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=crypto_profile_string.replace(",", " ").replace(".", ","))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Your crypto profile isn't set up, to set it up please type")


async def crypto_set_up_profile_start():
    pass


async def crypto_set_up_profile_not():
    pass


async def stop_crypto_set_up():
    pass

set_up_crypto_profile = ConversationHandler(
    entry_points=[
        MessageHandler("N", crypto_set_up_profile_not),
        MessageHandler("n", crypto_set_up_profile_not),
        MessageHandler("Y", crypto_set_up_profile_start),
        MessageHandler("y", crypto_set_up_profile_start)],
    states={},  # TODO
    fallbacks=[CommandHandler("stop"), stop_crypto_set_up]
)


class Menu_Filter(filters.MessageFilter):
    """Custom filter
    return True if it is currently desired menu state
    menu states:
    0- base menu
    1- in crypto menu
    2-TODO
    3-TODO
    ...
    """

    def __init__(self, menu: int):
        self.menu = menu

    def filter(self):
        """ if menu from database == desired menu"""
        return menu == self.menu


if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('crypto', crypto))
    application.add_handler(CommandHandler('stop', stop))

    application.run_polling()
