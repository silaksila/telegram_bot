import pickle
from functools import partial
import numpy as np
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from telegram.constants import ParseMode
from bot_package.menufilter import MenuFilter


class PredictLungCancer:
    def __init__(self):
        self.i = None
        self.information = list(range(23))
        self.max_value = [100, 2, 10]
        self.names = ['Age',
                      'Gender',
                      'Air Pollution',
                      'Alcohol use',
                      'Dust Allergy',
                      'Occupational Hazards',
                      'Genetic Risk',
                      'chronic Lung Disease',
                      'Balanced Diet',
                      'Obesity',
                      'Smoking',
                      'Passive Smoker',
                      'Chest Pain',
                      'Coughing of Blood',
                      'Fatigue',
                      'Weight Loss',
                      'Shortness of Breath',
                      'Wheezing',
                      'Swallowing Difficulty',
                      'Clubbing of Finger Nails',
                      'Frequent Cold',
                      'Dry Cough',
                      'Snoring']
        self.data_for_prediction = np.zeros((1, 23))

    def get_max_value(self, index):
        if index == 0:
            return 100
        elif index == 1:
            return 2
        else:
            return 10

    def predict_lung_cancer(self, ndarray: np.ndarray):
        """load model from txt file and return prediction
        return false if ndarray is incorrect shape"""

        if ndarray.shape != (1, 23):
            return False

        with open("bot_package/predict_lung_cancer.txt", "rb") as f:
            model = pickle.load(f)
        return model.predict(ndarray)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(text="Take this test to find out your risk of getting lung cancer"
        "\n""Lung cancer is the leading cause of cancer death worldwide, accounting for 1.59 million deaths in 2018.\n"
                                             "To cancel type /stop ")
        await update.message.reply_text(text="Please type your age: ", disable_notification=True)
        return 0

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(text="The test was closed", disable_notification=True)
        return ConversationHandler.END

    async def output_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE, index=None):
        last_input = update.message.text
        self.data_for_prediction[0][index] = int(last_input)
        if index != 22:
            name = self.names[index+1]
            # if question isn't gender
            if index != 0:
                reply_keyboard = [[str(i) for i in range(1, 11)]]
                await update.message.reply_text(text=f"{name} level:",
                                                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True), disable_notification=True)
            else:
                reply_keyboard = [["1", "2"]]
                await update.message.reply_text(text=f"{name}:\n1: Male\n2: Female",
                                                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True), disable_notification=True)

            return index + 1
        else:
            await update.message.reply_text(text=f"Your test is complete, here are your results:", disable_notification=True)
            prediction = self.predict_lung_cancer(self.data_for_prediction)
            await update.message.reply_text(text=f"Your chance of developing lung cancer in the future is: *{prediction}*",
                                            parse_mode=ParseMode.MARKDOWN_V2, disable_notification=True)
            return ConversationHandler.END

    def conversation_states(self):
        states = {}
        for i in range(len(self.information)):
            states[i] = [MessageHandler(filters.Text([str(j) for j in range(1, self.get_max_value(i)+1)]),
                                        partial(self.output_data, index=i))]
        return states

    def create_conversation_handler(self) -> ConversationHandler:
        conversation = ConversationHandler(
            entry_points=[MessageHandler(MenuFilter(command="/lungcancer"), self.start)],
            states=self.conversation_states(),
            fallbacks=[CommandHandler("stop", self.stop)])
        return conversation
