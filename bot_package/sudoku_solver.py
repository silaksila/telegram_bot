import cv2
import numpy as np
import pytesseract
import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from telegram.constants import ParseMode
from bot_package.menu_filter import Menu_Filter


class SudokuSolver:

    def __int__(self, board: np.ndarray):
        self.board = board

    # TODO vectorize this
    def check(self, y, x, n):
        # check rows
        for i in range(0, 9):
            if self.board[y][i] == n:
                return False
        # check columns
        for i in range(0, 9):
            if self.board[i][x] == n:
                return False
        x0 = (x // 3) * 3
        y0 = (y // 3) * 3
        # check 3*3 squares
        for i in range(0, 3):
            for j in range(0, 3):
                if self.board[y0 + i][x0 + j] == n:
                    return False
        return True

    def solve(self):
        for y in range(9):
            for x in range(9):
                if self.board[y][x] == 0:
                    for n in range(1, 10):
                        if self.check(y, x, n):
                            self.board[y][x] = n
                            self.solve()
                            self.board[y][x] = 0
                    return
        array = np.array(self.board)

    async def start(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        reply_keyboard = [["1.", "2."]]
        await update.message.reply_text(text=
                    "This tool will solve sudoku for you:\n1. Take a photo\n2. Manually fill in sudoku board",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return 0

    async def photo(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        # TODO
        pass

    async def manually_fill_board(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        # TODO
        return 1

    async def stop(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(text=" Stopped")
        return ConversationHandler.END

    def create_conversation_handler(self) -> ConversationHandler:
        conversation = ConversationHandler(
            entry_points=[MessageHandler(Menu_Filter(command="/sudoku"), self.start)],
            states={
                0: [MessageHandler(filters.Text(["1."]), self.photo),
                    MessageHandler(filters.Text(["2."]), self.manually_fill_board)],
                1: []
            },
            fallbacks=[CommandHandler("stop", self.stop)]
        )
        return conversation
