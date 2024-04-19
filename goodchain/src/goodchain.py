from user import User
from user_interface import UserInterface
from system import System


ui = UserInterface()
user = User()


def run_goodchain_app(node=None):
    """ Runs the GoodChain application """
    global ui, user
    user_is_logged_in = node is not None
    if user_is_logged_in:
        node.show_menu()
        node = node.handle_menu_user_input()
        input("Press enter to continue.")
    else:
        # Start the application with a public menu interface
        user.show_menu()
        node = user.handle_menu_user_input()

    ui.clear_console()
    return run_goodchain_app(node)


if __name__ == "__main__":
    system = System()
    if system.is_data_integrity_preserved():
        run_goodchain_app()
    else:
        exit()
