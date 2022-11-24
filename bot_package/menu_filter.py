from telegram import Message
from telegram.ext import filters
from bot_package.database_operations import reload_database, save_to_database

class Menu_Filter(filters.MessageFilter):
    """Custom filter
        return True if it is currently desired menu state
        menu states:
        0- base menu
        1- in crypto menu
        2- lung cancer prediction
        3-TODO
        ...
        """

    def __init__(self, command: str, menu_state):
        super().__init__()

        self.menu_state, self._ = reload_database()
        self.command = command
        self.menu_commands = [
            ["/start", "/crypto", "/stop", "/help", "/menu", "/lungcancer"],
            ["/profile", "/back", "/crypto", "/help", "/menu"],
            ["/edit", "/back", "/help", "/menu"],
            ["/help", "/menu"]
        ]

    def filter(self, message: Message) -> bool:
        """return True if the command is corresponding to the menu user is currently in"""
        self.menu_state, self._ = reload_database()
        if message.text == self.command:
            if message.text in self.menu_commands[self.menu_state]:
                return True
        return False

