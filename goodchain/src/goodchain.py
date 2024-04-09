# Imports
import os
import platform
from registration import registrate_user
from login import login


node = None


def clear_console():
    """ Clears the console screen for Windows, macOS and Linux. """
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def show_public_menu():
    """ Shows the public menu (meant for users that aren't logged in) """
    print("Goodchain Public Menu\n")
    print(
        "1 - Login\n"
        "2 - Explore the blockchain\n"
        "3 - Sign up\n"
        "4 - Exit\n"
    )


def handle_public_menu_user_input():
    """ Handles user input for the public menu interface """
    global node
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


def run_goodchain_app():
    """ Runs the goodchain application """
    global node
    # Start the application with a public menu interface
    show_public_menu()
    handle_public_menu_user_input()

    user_is_logged_in = node is not None
    if user_is_logged_in:
        # TODO: Set up private menu (meant for logged in users only)
        pass
    else:
        clear_console()
        return run_goodchain_app()


if __name__ == "__main__":
    run_goodchain_app()
