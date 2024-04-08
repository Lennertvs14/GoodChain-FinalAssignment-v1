import os
import platform
from registration import registrate_user
from login import login


def clear_console():
    """
    Clears the console screen for Windows, macOS and Linux.
    """
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


# Start the application with a public menu interface
print("Goodchain Public Menu\n")
print(
    "1 - Login\n"
    "2 - Explore the blockchain\n"
    "3 - Sign up\n"
    "4 - Exit\n"
)

chosen_menu_item = input("-> ")

try:
    chosen_menu_item = int(chosen_menu_item)
    match chosen_menu_item:
        case 1:
            clear_console()
            print("Login")
            node = login()
        case 2:
            clear_console()
            print("Explore the blockchain")
        case 3:
            clear_console()
            print("Sign up")
            registrate_user()
        case _:
            exit()
except ValueError:
    print("Enter digits only.")
