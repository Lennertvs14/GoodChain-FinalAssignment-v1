# Imports
from user import User
import transaction_pool
from ledger import Ledger
from user_interface import UserInterface


ui = UserInterface()
node = None
user = User()
ledger = Ledger()


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
                ui.clear_console()
                print("Profile")
                node.show_profile()
            case 2:
                ui.clear_console()
                print("Explore the blockchain")
                ledger.show_ledger()
            case 3:
                ui.clear_console()
                print("Send Coins")
                node.send_coins()
            case 4:
                ui.clear_console()
                print("Explore the transaction pool")
                transaction_pool.show_transaction_pool()
            case 5:
                ui.clear_console()
                print("Mine")
                node.mine()
            case 6:
                ui.clear_console()
                print("Transaction history")
                print(node.wallet.transactions)
            case 7:
                ui.clear_console()
                print("You're logged out, thanks for using GoodChain!")
                node = None
            case _:
                raise ValueError("Invalid choice.")
    except ValueError:
        print("Enter valid digits only.")


def run_goodchain_app():
    """ Runs the GoodChain application """
    global user, node
    user_is_logged_in = node is not None

    if user_is_logged_in:
        show_private_menu()
        handle_private_menu_user_input()
        input("Press enter to continue.")
    else:
        # Start the application with a public menu interface
        show_public_menu()
        handle_public_menu_user_input()
        user.show_menu()
        node = user.handle_public_menu_user_input()

    clear_console()
    ui.clear_console()
    return run_goodchain_app()


if __name__ == "__main__":
    run_goodchain_app()
