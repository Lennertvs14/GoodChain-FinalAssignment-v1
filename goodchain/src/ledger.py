import pickle
from transaction_block import TransactionBlock
from user_interface import UserInterface, whitespace


path = "../data/ledger.dat"


class Ledger:
    """ Represents a 'immutable' record of all transactions that have been executed and shared among nodes """

    @staticmethod
    def show_menu():
        """ Shows the ledger menu """
        print("Ledger Menu\n")
        print(
            "1 - View specific block by its number\n"
            "2 - View all blocks\n"
            "3 - View all blocks (paged)\n"
            "4 - View last block\n"
            "5 - Go back\n"
        )

    @staticmethod
    def handle_menu_input():
        """ Handles user input for the ledger menu interface """
        ui = UserInterface()
        chosen_menu_item = input("-> ")
        try:
            chosen_menu_item = int(chosen_menu_item)
            match chosen_menu_item:
                case 1:
                    ui.clear_console()
                    Ledger.show_block_by_id()
                case 2:
                    ui.clear_console()
                    Ledger.show_ledger()
                case 3:
                    ui.clear_console()
                    Ledger.show_ledger_paged()
                case 4:
                    ui.clear_console()
                    print(whitespace + f"{Ledger.get_last_block()}")
                case 5:
                    return
                case _:
                    raise ValueError("Invalid choice.")
        except ValueError:
            print("Enter digits only.")

        input("Press enter to continue.")

    @staticmethod
    def show_block_by_id():
        """ Prints a block by id"""
        blocks = Ledger.get_blocks()
        if blocks:
            chosen_block_id = input("\nEnter the ID of the block you'd like to validate:").strip()
            try:
                chosen_block_id = int(chosen_block_id)
                if 0 <= chosen_block_id < len(blocks):
                    chosen_block = blocks[chosen_block_id]
                    print(whitespace + f"{chosen_block}")
                else:
                    print("Invalid id, please try again.")
            except ValueError:
                if chosen_block_id == 'back':
                    return
                print("Invalid id, please try again.")

    @staticmethod
    def add_block(block: TransactionBlock):
        """ Adds transaction block to the ledger """
        if block:
            with open(path, "ab") as ledger:
                pickle.dump(block, ledger)

    @staticmethod
    def show_ledger():
        """ Prints out the current ledger """
        blocks = Ledger.get_blocks()
        if blocks is not None and len(blocks) > 0:
            print("Blocks:")
            for block in blocks:
                print(whitespace + f"{block}")
        else:
            print("There are no blocks in our chain yet.")

    @staticmethod
    def show_ledger_paged():
        all_blocks = Ledger.get_blocks()

        if all_blocks is None or len(all_blocks) < 1:
            print("No blocks in the ledger.")
            return

        current_part = 0
        part_size = 3

        while True:
            pages_length = len(all_blocks) // part_size + 1 if len(all_blocks) % part_size != 0 else len(all_blocks) // part_size

            print(f"Part {current_part + 1} of {pages_length}\n")

            for i in range(current_part * part_size, current_part * part_size + part_size):
                if i < len(all_blocks):
                    print(whitespace + f"{all_blocks[i]}")
                    print()
                else:
                    break

            print("1 - Next page")
            print("2 - Previous page")
            print("3 - Go back\n")

            choice = input("-> ")

            if choice == "1":
                if current_part < pages_length - 1:
                    current_part += 1
            elif choice == "2":
                if current_part > 0:
                    current_part -= 1
            elif choice == "3":
                break
            else:
                print("Invalid choice.")

    @staticmethod
    def get_blocks():
        """ Returns a list of blocks out of the ledger """
        blocks = []
        try:
            with open(path, "rb") as ledger:
                while True:
                    block = pickle.load(ledger)
                    blocks.append(block)
        except FileNotFoundError:
            # There is no ledger yet
            pass
        except EOFError:
            # No more lines to read from file
            pass
        return blocks

    @staticmethod
    def get_last_block():
        """ Returns the last block out of the ledger or None """
        all_blocks = Ledger.get_blocks()
        if all_blocks is not None and len(all_blocks) > 0:
            return all_blocks[-1]
        else:
            return None

    @staticmethod
    def update_block(updated_block: TransactionBlock):
        """ Updates the ledger with the passed block """
        blocks = Ledger.get_blocks()
        for i, block in enumerate(blocks):
            if block.id == updated_block.id:
                blocks[i] = updated_block
                break
        with open(path, "wb") as ledger:
            for block in blocks:
                pickle.dump(block, ledger)

    @staticmethod
    def remove_block(block_to_remove: TransactionBlock):
        """ Removes the passed block from the ledger """
        blocks = Ledger.get_blocks()
        blocks = [block for block in blocks if block.id != block_to_remove.id]
        with open(path, "wb") as ledger:
            for block in blocks:
                pickle.dump(block, ledger)
