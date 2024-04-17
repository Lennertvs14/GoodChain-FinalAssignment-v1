# Imports
from user import User
from user_interface import UserInterface

ui = UserInterface()
user = User()
node = None


def run_goodchain_app():
    """ Runs the GoodChain application """
    global user, node
    user_is_logged_in = node is not None

    if user_is_logged_in:
        node.show_menu()
        node.handle_menu_user_input()
        input("Press enter to continue.")
    else:
        # Start the application with a public menu interface
        user.show_menu()
        node = user.handle_menu_user_input()

    ui.clear_console()
    return run_goodchain_app()


if __name__ == "__main__":
    run_goodchain_app()
