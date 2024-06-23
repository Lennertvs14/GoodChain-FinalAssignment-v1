import os
import platform


WHITESPACE = "    "
TEXT_COLOR = {
    "PURPLE": '\033[95m',
    "BLUE": '\033[94m',
    "CYAN": '\033[96m',
    "GREEN": '\033[92m',
    "YELLOW": '\033[93m',
    "RED": '\033[91m'
}
TEXT_TYPE = {
    "BOLD": '\033[1m',
    "UNDERLINE": '\033[4m'
}


class UserInterface:
    """ Represents the console based user interface """
    def __init__(self):
        # INPUT
        self.INPUT_ARROW = self.format_text("-> ", TEXT_COLOR.get("YELLOW"))
        self.PRESS_ENTER_TO_CONTINUE = self.format_text("Press enter to continue.", text_type=TEXT_TYPE.get("BOLD"))

        # OUTPUT
        self.INVALID_MENU_ITEM = self.format_text("Invalid menu item.", TEXT_COLOR.get("RED"))
        self.ENTER_DIGITS_ONLY = self.format_text("Enter digits only.", TEXT_COLOR.get("RED"))
        self.INVALID_ID = self.format_text("Invalid id, please try again.", TEXT_COLOR.get("RED"))

        self.BACK = self.format_text('back', text_type=TEXT_TYPE.get("BOLD"))
        self.ERROR = self.format_text("An unexpected error occurred.", text_color=TEXT_COLOR.get("RED"))

    @staticmethod
    def clear_console():
        """ Clears the console screen for Windows, macOS and Linux. """
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    @staticmethod
    def format_text(text, text_color='', text_type=''):
        end_text_formatting = '\033[0m'
        return f"{text_color}{text_type}{text}{end_text_formatting}"
