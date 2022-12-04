from telegram import Message
from telegram.ext import filters
from bot_package.database_operations import reload_database, save_to_database


class MenuFilter(filters.MessageFilter):
    """Custom filter
        return True if it is currently desired menu state
        dic explained:
        0- base menu - only work in base menu
        1- in crypto menu - only work in crypto menu
        2- will work anywhere
        ...
        """

    def __init__(self, command: str):
        super().__init__()

        self.menu_state, self.data = None, None
        self.command = command
        self.menu_commands = {
            0: ["/start", "/crypto", "/lungcancer", "/sudoku"],
            1: ["/profile", "/crypto"],
            2: ["/menu"]}

    def filter(self, message: Message) -> bool:
        """return True if the command is corresponding to the menu user is currently in"""
        self.menu_state, self.data = reload_database(message.chat_id)
        if message.text == self.command:
            if message.text in self.menu_commands[self.menu_state] or message.text in self.menu_commands[2]:
                if message.text == "/crypto":
                    save_to_database(1, self.data, message.chat_id)
                elif message.text == "/menu":
                    save_to_database(0, self.data, message.chat_id)
                return True
        return False
