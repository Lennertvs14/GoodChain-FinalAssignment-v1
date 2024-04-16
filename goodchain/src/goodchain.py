# Imports
import os
import platform
from registration import registrate_user
from login import login
import transaction_pool


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
            case 4:
                exit()
            case _:
                raise ValueError("Invalid choice.")
    except ValueError:
        print("Enter digits only.")


def show_private_menu():
    """ Shows the private menu (meant for nodes only) """
    print("Welcome \n")
    print(
        "1 - Profile\n"
        "2 - Explore the blockchain\n"
        "3 - Send coins\n"
        "4 - Explore the transaction pool\n"
        "5 - Mine\n"
        "6 - Show transaction history\n"
        "7 - Log out\n"
    )


def handle_private_menu_user_input():
    """ Handles node input for the private menu interface """
    global node
    chosen_menu_item = input("-> ")
    try:
        chosen_menu_item = int(chosen_menu_item)
        match chosen_menu_item:
            case 1:
                clear_console()
                print("Profile")
                node.show_profile()
            case 2:
                clear_console()
                print("Explore the blockchain")
            case 3:
                clear_console()
                print("Send Coins")
                node.send_coins()
            case 4:
                clear_console()
                print("Explore the transaction pool")
                transaction_pool.check_pool()
            case 5:
                clear_console()
                print("Mine")
                node.mine()
            case 6:
                clear_console()
                print("Transaction history")
                print(node.wallet.transactions)
            case 7:
                clear_console()
                print("You're logged out, thanks for using GoodChain!")
                node = None
            case _:
                raise ValueError("Invalid choice.")
    except ValueError:
        print("Enter valid digits only.")


def run_goodchain_app():
    """ Runs the goodchain application """
    global node
    user_is_logged_in = node is not None

    if user_is_logged_in:
        show_private_menu()
        handle_private_menu_user_input()
        input("Press enter to continue.")
    else:
        # Start the application with a public menu interface
        show_public_menu()
        handle_public_menu_user_input()

    clear_console()
    return run_goodchain_app()


if __name__ == "__main__":
    run_goodchain_app()
