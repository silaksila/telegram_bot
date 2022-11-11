import logging
import threading
import requests
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
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
    # get crypto price from binance api
    urls = [key+name+"USDT" for name in crypto_names]
    prices = [requests.get(url).json() for url in urls]
    btc_price = float(prices[0]["price"])
    string = ""
    if data["crypto"]["setup"]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*Current state:* \n", parse_mode=ParseMode.MARKDOWN_V2)
        for indx, val in enumerate(prices):
            crypto_price = float(val["price"])
            difference_to_old_price = (
                (crypto_price/crypto_amounts[indx][1])-1)*100
            string += (
                f"{crypto_names[indx]} : {crypto_price:,.2f} $  {difference_to_old_price:+.2f} %\n")
            data["crypto"]["coins"][crypto_names[indx]][1] = crypto_price

        with open("database.json", "w") as file:
            json.dump(data, file)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=string.replace(",", " ").replace(".", ","))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your crypto profile:\n {crypto_names[0]} : {crypto_amounts[0][0]*btc_price:.2f}. $ ".replace(".", ","))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Your crypto profile isn't set up, do you wish to set it up right now ?Y/N")


if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('crypto', crypto))
    application.add_handler(CommandHandler('stop', stop))

    application.run_polling()
