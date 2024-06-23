from system import System
from user import User
from user_interface import UserInterface

user = None


def run_goodchain_app(node=None):
    """ Runs the GoodChain application """
    global user
    user_is_logged_in = node is not None

    try:
        if user_is_logged_in:
            node.show_menu()
            node = node.handle_menu_user_input()
            input("\n" + UserInterface().PRESS_ENTER_TO_CONTINUE)
        else:
            # Start the application with a public menu interface
            user.show_menu()
            node = user.handle_menu_user_input()
    except Exception as exception:
        from os import makedirs, path
        makedirs(path.dirname("../logs/incidents.txt"), exist_ok=True)
        with open("../logs/incidents.txt", "at") as log_file:
            # Add unexpected error to logs so one can share it with helpdesk if necessary
            log_file.write(f"{repr(exception)}\n")
        node.log_out()
        node = None
        temp_ui = UserInterface()
        input(temp_ui.ERROR + "\n\n" + temp_ui.PRESS_ENTER_TO_CONTINUE)

    UserInterface.clear_console()
    return run_goodchain_app(node)


if __name__ == "__main__":
    system = System()
    if system.is_data_integrity_preserved():
        user = User()
        run_goodchain_app()
