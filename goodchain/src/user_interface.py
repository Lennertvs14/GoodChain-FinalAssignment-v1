import os
import platform


class UserInterface:
    """ Represents the console based user interface """
    @staticmethod
    def clear_console():
        """ Clears the console screen for Windows, macOS and Linux. """
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
