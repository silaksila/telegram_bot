import requests
import json
import re
import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from telegram.constants import ParseMode
from bot_package.menu_filter import Menu_Filter
from bot_package.database_operations import reload_database, save_to_database


class Crypto:

    def __init__(self, menu, data) -> None:
        self.run_job = True
        self.menu_state = menu
        self.data = data
        self.key = "https://api.binance.com/api/v3/ticker/price?symbol="
        self.SHOW_PROFILE, self.COINS, self.NOTIFICATION = range(3)
        self.notification = ["No notification", "Everyday", "Every 12 hours", "Every 6 hours",
                             "Every 3 hours", "Every hour", "Every half hour", "Every 15 minutes"]

        self.empty_data_base = {"crypto": {
            "setup": False, "coins": {}, "notifications": 0}, "menu": self.menu_state}
        self.allowed_coins = ["BTC", "ETH", "USDT", "USDC", "BNB", "BUSD", "XRP", "DOGE", "ADA", "MATIC",
                              "DOT", "DAI", "SHIB", "SQL", "TRX", "LTC", "UNI", "LEO", "AVAX", "WBTC", "LINK", "ATOM",
                              "ETC"]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            [str(i + 1) + "." for i in range(len(self.notification))]]
        for inx, notif in enumerate(self.notification):
            strg += f"{inx + 1}. {notif}\n"
        await update.message.reply_text("Done")
        await update.message.reply_text(text="How often do you wish to receive notification ?",
                                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        await update.message.reply_text(text=strg)
        return self.NOTIFICATION

    async def get_notifications(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.empty_data_base["crypto"]["notifications"] = int(
            update.message.text[0]) - 1
        self.empty_data_base["crypto"]["setup"] = True
        with open("database.json", "w") as f:
            json.dump(self.empty_data_base, f)
        # this will rerun job
        self.run_job = True
        self.menu_state, self.data = reload_database()
        self.load_job(update, context)
        await update.message.reply_text(text=f"Notification: {self.notification[int(update.message.text[0]) - 1]}",
                                        reply_markup=ReplyKeyboardRemove())
        await update.message.reply_text(text="Your crypto profile was successfully created")
        return ConversationHandler.END

    async def stop_set_up(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(text=f"Your profile wasn't saved")
        return ConversationHandler.END

    async def crypto_job(self, context: ContextTypes.DEFAULT_TYPE):
        job = context.job
        self.menu_state, self.data = reload_database()
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
                    f"{name} : {amount * curr_price:.2f}. $ \n")
                self.data["crypto"]["coins"][name][1] = curr_price
            text = f"*Current state:* \n{curr_state_string}\n*Your crypto profile:*\n{crypto_profile_string} ".replace(
                ",", " ").replace(".", ",").replace("+", "\\+").replace("-", "\\-")  # string escaping
            await context.bot.send_message(chat_id=job.chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)

            with open("database.json", "w") as file:  # write new price values to file
                json.dump(self.data, file)

    async def crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.menu_state, self.data = reload_database()
        self.menu_state = 1
        # get data from database,
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
                        f"{name} : {amount * curr_price:.2f}. $ \n")
                    self.data["crypto"]["coins"][name][1] = curr_price

                text = f"*Current state:* \n{curr_state_string}\n*Your crypto profile:*\n{crypto_profile_string} ".replace(
                    ",", " ").replace(".", ",").replace("+", "\\+").replace("-", "\\-")  # string escaping
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                                               parse_mode=ParseMode.MARKDOWN_V2)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="Your crypto profile isn't set up, to set it up please type /profile")

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="To return to the main menu please type /menu\nTo edit your crypto profile type /profile ")

        self.data["menu"] = self.menu_state
        with open("database.json", "w") as file:  # write new price values to file
            json.dump(self.data, file)

    def create_crypto_conversation(self):
        crypto_profile_conversation_handler = ConversationHandler(
            entry_points=[MessageHandler(Menu_Filter(
                command="/profile", menu_state=self.menu_state), self.start)],
            states={
                self.SHOW_PROFILE: [
                    MessageHandler(filters.Text(["Yes"]), self.start_edit),
                    MessageHandler(filters.Text(["No"]), self.stop_set_up)],
                self.COINS: [MessageHandler(
                    ~filters.Text(["Done", "done", "/skip"]), self.coins_input),
                    MessageHandler(filters.Text(["Done", "done", "skip"]), self.coins_done)],
                self.NOTIFICATION: [MessageHandler(filters.Text(
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
                curr_time = datetime.datetime.now()  # get current time
                curr_time = curr_time
                # every 24 hours
                if notification == 1:
                    first_time = curr_time.replace(second=0, microsecond=0, minute=0, hour=6)
                # every 12 hours
                elif notification == 2:
                    if curr_time.hour > 12:
                        hour = 0
                    else:
                        hour = 12
                    first_time = curr_time.replace(second=0, microsecond=0, minute=0, hour=hour)
                # every 6 hours
                elif notification == 3:
                    if curr_time.hour > 18:
                        hour = 0
                    else:
                        hour = ((curr_time.hour // 6) + 1) * 6
                    first_time = curr_time.replace(second=0, microsecond=0, minute=0, hour=hour)
                # every 3 hours
                elif notification == 4:
                    if curr_time.hour > 21:
                        hour = 0
                    else:
                        hour = ((curr_time.hour // 3) + 1) * 3
                    first_time = curr_time.replace(second=0, microsecond=0, minute=0, hour=hour)
                # every hour
                elif notification == 5:
                    first_time = curr_time.replace(second=0, microsecond=0, minute=0,
                                                   hour=curr_time.hour) + datetime.timedelta(
                        hours=1)

                # every 30 minutes
                elif notification == 6:
                    if curr_time.minute > 30:
                        first_time = curr_time.replace(second=0, microsecond=0, minute=0,
                                                       hour=curr_time.hour) + datetime.timedelta(
                            hours=1)
                    else:
                        first_time = curr_time.replace(second=0, microsecond=0, minute=30, hour=curr_time.hour)

                # every 15 minutes
                else:
                    if curr_time.minute > 45:
                        first_time = curr_time.replace(second=0, microsecond=0, minute=0,
                                                       hour=curr_time.hour) + datetime.timedelta(hours=1)
                    else:
                        minutes = ((curr_time.minute // 15) + 1) * 15
                        first_time = curr_time.replace(second=0, microsecond=0, minute=minutes, hour=curr_time.hour)

                # remove existing job from queue if exits
                current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
                if current_jobs:
                    for job in current_jobs:
                        job.schedule_removal()
                # add job to queue
                context.job_queue.run_repeating(
                    self.crypto_job, interval=intervals[notification - 1], first=first_time, chat_id=chat_id,
                    name=str(chat_id))

                self.run_job = False