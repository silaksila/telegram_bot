import requests
import re
import datetime
from sys import version_info
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from telegram.constants import ParseMode
from bot_package.menufilter import MenuFilter
from bot_package.database_operations import reload_database, save_to_database

if version_info.minor < 9:
    from backport.zoneinfo import ZoneInfo
else:
    from zoneinfo import ZoneInfo


def assign_time(curr_time: datetime.datetime, notification: int):
    """get the closest time depending on notification:
    1: closest 24 horus
    2: closest 12 hours
    3: closest 6 hours
    4: closest 3 hours
    5: closest 1 hour
    6: closest 30 minutes
    7: closest 15 minutes
    """
    intervals = [24, 12, 6, 3, 1, 0.5, 0.25]
    interval = intervals[notification - 1]
    if interval >= 1:
        next_time = curr_time.replace(second=0, microsecond=0, minute=0, hour=0)
        next_time += datetime.timedelta(hours=interval)
        while next_time <= curr_time:
            next_time += datetime.timedelta(hours=interval)

    else:
        minutes = int(60 * interval)
        next_time = curr_time.replace(second=0, microsecond=0, minute=minutes, hour=curr_time.hour)
        while next_time <= curr_time:
            next_time += datetime.timedelta(minutes=minutes)
    return next_time


class Crypto:

    def __init__(self) -> None:
        self.run_job = True
        self.menu_state = None
        self.data = None
        self.key = "https://api.binance.com/api/v3/ticker/price?symbol="
        self.notification = ["No notification", "Everyday", "Every 12 hours", "Every 6 hours",
                             "Every 3 hours", "Every hour", "Every half hour", "Every 15 minutes"]

        self.empty_data_base = {"crypto": {
            "setup": False, "coins": {}, "notifications": 0}, "menu": 1}
        self.allowed_coins = ["BTC", "ETH", "USDT", "USDC", "BNB", "BUSD", "XRP", "DOGE", "ADA", "MATIC",
                              "DOT", "DAI", "SHIB", "SQL", "TRX", "LTC", "UNI", "LEO", "AVAX", "WBTC", "LINK", "ATOM",
                              "ETC"]

    async def start(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        self.menu_state, self.data = reload_database(update.message.chat_id)
        curr_notification = self.notification[self.data["crypto"]["notifications"]]
        reply_keyboard = [["Yes", "No"]]
        d = list(self.data["crypto"]["coins"])
        if self.data["crypto"]["setup"]:
            txt = f"*Settings:*\nCoins: {d}\nNotifications: {curr_notification}\n\nWant to recreate your profile ?"
        else:
            txt = "Create crypto profile ?"
        await update.message.reply_text(text=txt, parse_mode=ParseMode.MARKDOWN_V2,
                                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                         input_field_placeholder="Yes or No"))
        return 0

    async def start_edit(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(text=f"To cancel type /stop", disable_notification=True)
        await update.message.reply_text(text=f"To skip type /skip", disable_notification=True)
        await update.message.reply_text(text=f"When you are finished type Done", disable_notification=True)
        await update.message.reply_text(text=f"Please write your coins and amount: (ETH: 1,8)",
                                        disable_notification=True)
        return 1

    async def coins_input(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        inp_txt = update.message.text.replace(",", ".")
        if "." in inp_txt:  # if the number is float:
            num = re.findall("\d+\.\d+", inp_txt)  # find float number
        else:
            num = re.findall("\d+", inp_txt)  # find int
        if not num:
            await update.message.reply_text("Please write the number correctly", disable_notification=True)
        else:
            num = float(num[0])
            upper = "".join([c.upper() for c in inp_txt if c.isalpha()])
            if upper not in self.allowed_coins:
                await update.message.reply_text("Please write your coin correctly", disable_notification=True)
            else:
                self.empty_data_base["crypto"]["coins"][upper] = [num, None]
                await update.message.reply_text(f"Successfully added {upper}", disable_notification=True)

    async def coins_done(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        # if skipped
        if update.message.text == '/skip':
            self.empty_data_base['crypto']['coins'] = self.data['crypto']['coins']

        if not self.empty_data_base['crypto']['coins']:
            await update.message.reply_text(text="You didn't add any coins", disable_notification=True)

        # list all possible notification settings
        string = ""
        reply_keyboard = [
            [str(i + 1) + "." for i in range(len(self.notification))]]
        for inx, notif in enumerate(self.notification):
            string += f"{inx + 1}. {notif}\n"

        await update.message.reply_text(text="How often do you wish to receive notification ?",
                                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
                                        disable_notification=True)
        await update.message.reply_text(text=string, disable_notification=True)
        return 2

    async def get_notifications(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.empty_data_base["crypto"]["notifications"] = int(
            update.message.text[0]) - 1
        self.empty_data_base["crypto"]["setup"] = True
        save_to_database(self.menu_state, self.empty_data_base, update.message.chat_id, clear_coins_data=True)
        # rerun job
        self.run_job = True
        self.menu_state, self.data = reload_database(update.message.chat_id)
        self.load_job(update, context)

        await update.message.reply_text(text=f"Notification: {self.notification[int(update.message.text[0]) - 1]}",
                                        reply_markup=ReplyKeyboardRemove(), disable_notification=True)
        await update.message.reply_text(text="Your crypto profile was successfully created")
        return ConversationHandler.END

    async def stop_set_up(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(text=f"Your profile wasn't saved")
        return ConversationHandler.END

    async def crypto_job(self, context: ContextTypes.DEFAULT_TYPE):
        """Run everytime crypto report is called from job queue"""
        job = context.job
        self.menu_state, self.data = reload_database(context.job.chat_id)
        # get data from database,
        crypto = self.data["crypto"]["coins"]
        if not crypto:
            await context.bot.send_message(job.chat_id,
                                           text="You dont have any coins added, to add coins type /profile")
        else:
            crypto_amounts = list(crypto.values())
            crypto_names = list(crypto.keys())

            # get crypto price from binance api
            urls = [self.key + name + "USDT" for name in crypto_names]
            prices = [requests.get(url).json() for url in urls]

            crypto_profile_string = ""
            curr_state_string = ""
            for name, amount_and_old_price, curr_price in zip(crypto_names, crypto_amounts, prices):
                curr_price = float(curr_price["price"])
                amount, old_price = amount_and_old_price
                if not old_price:
                    old_price = curr_price
                difference_to_old_price = (
                                                  (curr_price / old_price) - 1) * 100
                curr_state_string += (
                    f"{name} : {curr_price:,.2f} $  {difference_to_old_price:+.2f} %\n")

                crypto_profile_string += (
                    f"{name} : {amount * curr_price:,.2f} $ \n")
                self.data["crypto"]["coins"][name][1] = curr_price
            text = f"*Current state:* \n{curr_state_string}\n*Your crypto profile:*\n{crypto_profile_string} ".replace(
                ",", " ").replace(".", ",").replace("+", "\\+").replace("-", "\\-")  # string escaping
            await context.bot.send_message(chat_id=job.chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)

            save_to_database(self.menu_state, self.data, job.chat_id)

    async def crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # get data from database
        self.menu_state, self.data = reload_database(update.message.chat_id)
        crypto = self.data["crypto"]["coins"]
        if not crypto:
            await context.bot.send_message(update.effective_chat.id,
                                           text="You dont have any coins added, to add coins type /profile")
        else:
            crypto_amounts = list(crypto.values())
            crypto_names = list(crypto.keys())

            if self.data["crypto"]["setup"]:
                # get crypto price from binance api
                urls = [self.key + name + "USDT" for name in crypto_names]
                prices = [requests.get(url).json() for url in urls]

                crypto_profile_string = ""
                curr_state_string = ""
                for name, amount_and_old_price, curr_price in zip(crypto_names, crypto_amounts, prices):
                    curr_price = float(curr_price["price"])
                    amount, old_price = amount_and_old_price
                    if not old_price:
                        old_price = curr_price
                    difference_to_old_price = (
                                                      (curr_price / old_price) - 1) * 100
                    curr_state_string += (
                        f"{name} : {curr_price:,.2f} $  {difference_to_old_price:+.2f} %\n")

                    crypto_profile_string += (
                        f"{name} : {amount * curr_price:,.2f} $ \n")
                    self.data["crypto"]["coins"][name][1] = curr_price

                text = f"*Current state:* \n{curr_state_string}\n*Your crypto profile:*\n{crypto_profile_string} ".replace(
                    ",", " ").replace(".", ",").replace("+", "\\+").replace("-", "\\-")  # string escaping
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                                               parse_mode=ParseMode.MARKDOWN_V2)

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="To return to the main menu please type /menu\nTo edit your crypto profile type /profile ",
                                       disable_notification=True)

        save_to_database(self.menu_state, self.data, update.message.chat_id)

    def create_crypto_conversation(self) -> ConversationHandler:
        crypto_profile_conversation_handler = ConversationHandler(
            entry_points=[MessageHandler(MenuFilter(
                command="/profile"), self.start)],
            states={
                0: [
                    MessageHandler(filters.Text(["Yes"]), self.start_edit),
                    MessageHandler(filters.Text(["No"]), self.stop_set_up)],
                1: [MessageHandler(
                    ~filters.Text(["Done", "done", "DONE", "/skip"]), self.coins_input),
                    MessageHandler(filters.Text(["Done", "done", "DONE", "/skip"]), self.coins_done)],
                2: [MessageHandler(filters.Text(
                    [str(i + 1) + "." for i in range(len(self.notification))]),
                    self.get_notifications)]
            },
            fallbacks=[CommandHandler("stop", self.stop_set_up)])
        return crypto_profile_conversation_handler

    def load_job(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.run_job:
            chat_id = update.effective_message.chat_id
            notification = self.data["crypto"]["notifications"]
            if notification != 0:
                # intervals 24hours, 12hours, 6hours,3 hours, 1 hour, half hour, 15 minutes
                intervals = [86400, 43200, 21600, 10800, 3600, 1800, 900, 30]
                # remove existing job from queue if exits
                current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
                if current_jobs:
                    for job in current_jobs:
                        job.schedule_removal()

                curr_time = datetime.datetime.now(tz=ZoneInfo('Europe/Berlin'))  # get current time
                time = assign_time(curr_time, notification)
                # add job to queue
                context.job_queue.run_repeating(
                    self.crypto_job, interval=intervals[notification - 1], first=time, chat_id=chat_id,
                    name=str(chat_id))

                self.run_job = False
