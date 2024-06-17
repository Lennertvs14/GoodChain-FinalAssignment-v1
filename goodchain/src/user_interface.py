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
