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
key = "https://api.binance.com/api/v3/ticker/price?symbol="

with open("database.json") as f:
    data = json.load(f)
data["menu"] = 0  # !temporary
menu_state = data["menu"]


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

    def __init__(self, command: str):
        super().__init__()

        self.command = command
        self.menu_commands = [
            ["/start", "/crypto", "/stop",  "/help", "/menu"],
            ["/profile", "/back", "/crypto", "/help", "/menu"],
            ["/edit", "/back", "/help", "/menu"]
        ]
        with open("database.json") as f:
            self.menu_state = json.load(f)["menu"]

    def filter(self, message: Message) -> bool:
        """return True if the command is corresponding to the menu user is currently in"""
        if message.text == self.command:
            if message.text in self.menu_commands[menu_state]:
                return True
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Hello, please type /help to show all commands")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="*Commands:* ", parse_mode=ParseMode.MARKDOWN_V2)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="/crypto - show your crypto profile \n/menu - go back to the menu")


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global menu_state
    menu_state = 0
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Main menu")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Unknown command, type /help to show all commands")


async def crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global menu_state
    menu_state = 1
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
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Your crypto profile isn't set up, to set it up please type /profile")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="To return to the main menu please type /menu\nTo edit your crypto profile type /profile ")


async def edit_crypto_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def crypto_set_up_profile_start():
    pass


async def crypto_set_up_profile_not():
    pass


async def stop_crypto_set_up():
    pass

# crypto_profile = ConversationHandler(
 #   entry_points=[MessageHandler(Menu_Filter(
  #      command="/profile"), edit_crypto_profile)],
   # states={},  # TODO
    # fallbacks=[CommandHandler("stop"), stop_crypto_set_up])


def main():
    application = ApplicationBuilder().token(token).build()
    application.add_handler(MessageHandler(
        Menu_Filter(command="/start"), start))
    application.add_handler(MessageHandler(
        Menu_Filter(command="/crypto"), crypto))
    application.add_handler(MessageHandler(
        Menu_Filter(command="/help"), help))
    application.add_handler(MessageHandler(
        Menu_Filter(command="/menu"), menu))

    application.add_handler(MessageHandler(
        filters.MessageFilter, unknown_command))

    application.run_polling()


if __name__ == '__main__':
    main()
