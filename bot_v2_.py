import logging
import requests
import json
import re
import datetime
from telegram import Update, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ParseMode

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
token = "5788908830:AAGew0qIRF3l3TxR57Lcf4egiwbBU1XuBdo"
key = "https://api.binance.com/api/v3/ticker/price?symbol="


# TODO create reload func for database
# TODO every x hour reply with crypto
menu_state = 0  # !temporary


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


class Crypto_profile_conversation():
    global menu_state

    def __init__(self) -> None:
        self.SHOW_PROFILE, self.COINS, self.NOTIFICATION = range(
            3)
        self.notification = ["No notification", "Everyday", "Every 6 hours", "Every 3 hours",
                             "Every hour", "Every half hour", "Every 15 minutes"]

        self.empty_data_base = {"crypto": {
            "setup": False, "coins": {}, "notifications": 0}, "menu": menu_state}
        self.allowed_coins = ["BTC", "ETH", "USDT", "USDC", "BNB", "BUSD", "XRP", "DOGE", "ADA", "MATIC",
                              "DOT", "DAI", "SHIB", "SQL", "TRX", "LTC", "UNI", "LEO", "AVAX", "WBTC", "LINK", "ATOM", "ETC"]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print("Lol")
        curr_notification = self.notification[data["crypto"]["notifications"]]
        reply_keyboard = [["Yes", "No"]]
        d = list(data["crypto"]["coins"])
        if data["crypto"]["setup"]:
            txt = f"*Settings:*\nCoins: {d}\nNotifications: {curr_notification}\n\nWant to recreate your profile ?"
        else:
            txt = "Create crypto profile ?"
        await update.message.reply_text(text=txt, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="Yes or No"))
        return self.SHOW_PROFILE

    async def start_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(text=f"To cancel type /stop")
        await update.message.reply_text(text=f"To skip type /skip")
        await update.message.reply_text(text=f"When you are finished type Done")
        await update.message.reply_text(text=f"Please write your coins and amount: (ETH: 1,8)")
        return self.COINS

    async def coins_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        input = update.message.text.replace(",", ".")
        if "." in input:  # if the number is float:
            num = re.findall("\d+\.\d+", input)  # find float number
        else:
            num = re.findall("\d+", input)  # find int
        if not num:
            await update.message.reply_text("Please write the number correctly")
        else:
            num = float(num[0])
            upper = "".join([c for c in input if c.isupper()])
            if upper not in self.allowed_coins:
                await update.message.reply_text("Please write your coin correctly")
            else:
                self.empty_data_base["crypto"]["coins"][upper] = [num, None]
                await update.message.reply_text(f"Successfully added {upper}")

    async def coins_done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        strg = ""
        reply_keyboard = [
            [str(i+1)+"." for i in range(len(self.notification))]]
        for inx, notif in enumerate(self.notification):
            strg += f"{inx+1}. {notif}\n"
        await update.message.reply_text("Done")
        await update.message.reply_text(text="How often do you wish to receive notification ?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        await update.message.reply_text(text=strg)
        return self.NOTIFICATION

    async def get_notifications(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.empty_data_base["crypto"]["notification"] = int(
            update.message.text[0])-1
        self.empty_data_base["crypto"]["setup"] = True
        with open("database.json", "w") as f:
            json.dump(self.empty_data_base, f)
        await update.message.reply_text(text=f"Notification:{self.notification[int(update.message.text[0])-1]}")
        await update.message.reply_text(text="Your crypto profile was successfully created")
        return ConversationHandler.END

    async def stop_set_up(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(text=f"Your profile wasn't saved")
        return ConversationHandler.END


def reload_database():
    global menu_state, data
    with open("database.json") as f:
        data = json.load(f)
    menu_state = data["menu"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    notification = data["crypto"]["notification"]
    if notification != 0:
        intervals = [86400, 21600, 3600, 1800,
                     900, 450, 30]  # intervals in seconds
        now = datetime.datetime.now()
        year, month, day, hour, minute, _, _, _, _ = now.timetuple()
        if notification == 1:
            day += 1
            hour = 6
        date = datetime.datetime(2022, 11, 19, 5, 18)
        context.job_queue.run_repeating(
            crypto_job, interval=intervals[6], first=data, chat_id=chat_id, name=str(chat_id))  # ! edit time

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


async def crypto_job(context: ContextTypes.DEFAULT_TYPE):
    global menu_state
    job = context.job
    reload_database()
    menu_state = 1
    # get data from database,
    crypto = data["crypto"]["coins"]
    if not crypto:
        await context.bot.send_message(job.chat_id, text="You dont have any coins added, to add coins type /profile")
    else:
        crypto_amounts = list(crypto.values())
        crypto_names = list(crypto.keys())

        # get crypto price from binance api
        urls = [key+name+"USDT" for name in crypto_names]
        prices = [requests.get(url).json() for url in urls]

        crypto_profile_string = ""
        curr_state_string = ""
        for name, amount_and_old_price, curr_price in zip(crypto_names, crypto_amounts, prices):
            curr_price = float(curr_price["price"])
            amount, old_price = amount_and_old_price
            if old_price == None:
                old_price = curr_price
            difference_to_old_price = (
                (curr_price/old_price)-1)*100
            curr_state_string += (
                f"{name} : {curr_price:,.2f} $  {difference_to_old_price:+.2f} %\n")

            crypto_profile_string += (
                f"{name} : {amount*curr_price:.2f}. $ \n")
            data["crypto"]["coins"][name][1] = curr_price
        text = f"*Current state:* \n{curr_state_string}\n*Your crypto profile:*\n{crypto_profile_string} ".replace(
            ",", " ").replace(".", ",").replace("+", "\\+").replace("-", "\\-")  # string escaping
        await context.bot.send_message(chat_id=job.chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)

        with open("database.json", "w") as file:  # write new price values to file
            json.dump(data, file)


async def crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global menu_state
    reload_database()
    menu_state = 1
    # get data from database,
    crypto = data["crypto"]["coins"]
    if not crypto:
        await context.bot.send_message(update.effective_chat.id, text="You dont have any coins added, to add coins type /profile")
    else:
        crypto_amounts = list(crypto.values())
        crypto_names = list(crypto.keys())

    if data["crypto"]["setup"]:
        # get crypto price from binance api
        urls = [key+name+"USDT" for name in crypto_names]
        prices = [requests.get(url).json() for url in urls]

        crypto_profile_string = ""
        curr_state_string = ""
        for name, amount_and_old_price, curr_price in zip(crypto_names, crypto_amounts, prices):
            curr_price = float(curr_price["price"])
            amount, old_price = amount_and_old_price
            if old_price == None:
                old_price = curr_price
            difference_to_old_price = (
                (curr_price/old_price)-1)*100
            curr_state_string += (
                f"{name} : {curr_price:,.2f} $  {difference_to_old_price:+.2f} %\n")

            crypto_profile_string += (
                f"{name} : {amount*curr_price:.2f}. $ \n")
            data["crypto"]["coins"][name][1] = curr_price

        text = f"*Current state:* \n{curr_state_string}\n*Your crypto profile:*\n{crypto_profile_string} ".replace(
            ",", " ").replace(".", ",").replace("+", "\\+").replace("-", "\\-")  # string escaping
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Your crypto profile isn't set up, to set it up please type /profile")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="To return to the main menu please type /menu\nTo edit your crypto profile type /profile ")

    with open("database.json", "w") as file:  # write new price values to file
        json.dump(data, file)


crypto_profile_class = Crypto_profile_conversation()
crypto_profile_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Menu_Filter(
        command="/profile"), crypto_profile_class.start)],
    states={
        crypto_profile_class.SHOW_PROFILE: [MessageHandler(filters.Text(["Yes"]), crypto_profile_class.start_edit), MessageHandler(filters.Text(["No"]), crypto_profile_class.stop_set_up)],
        crypto_profile_class.COINS: [MessageHandler(
            ~filters.Text(["Done", "done", "/skip"]), crypto_profile_class.coins_input), MessageHandler(filters.Text(["Done", "done", "skip"]), crypto_profile_class.coins_done)],
        crypto_profile_class.NOTIFICATION: [MessageHandler(filters.Text(
            [str(i+1)+"." for i in range(len(crypto_profile_class.notification))]), crypto_profile_class.get_notifications)]
    },  # TODO
    fallbacks=[CommandHandler("stop", crypto_profile_class.stop_set_up)])


def main():
    global data, menu_state
    reload_database()
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
        filters.MessageFilter(), unknown_command))
    application.add_handler(crypto_profile_conversation_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
