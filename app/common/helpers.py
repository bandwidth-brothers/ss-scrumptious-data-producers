import os

from app.users.model import User
from app.orders.model import Order
from app.users.formatter import UserFormatter
from app.orders.formatter import OrderFormatter


class Formatters:
    _MAP = {
        User: UserFormatter(),
        Order: OrderFormatter()
    }

    @staticmethod
    def for_type(cls):
        try:
            return Formatters._MAP[cls]
        except KeyError:
            return None


def print_items_and_confirm(items: list, item_type: str, print_limit: int = 10,
                            short: bool = False, pretty: bool = False) -> str:
    """
    Print the items to be inserted into the database (up to a limit)
    abd request for confirmation.

    :param items: the items to be printed
    :param item_type: the type of item that will be created
    :param print_limit: how many items (max) should be printed
    :param short: print short output for items
    :param pretty: print pretty output for items
    :return: the input from the user
    """
    print(f"The following {item_type} will be created:", end=os.linesep * 2)

    for i in range(len(items)):
        if i >= print_limit:
            break
        item = items[i]
        if short or pretty:
            formatter = Formatters.for_type(type(item))
            if short and formatter is not None:
                print(f"  {formatter.short(item)}")
                continue
            elif pretty and formatter is not None:
                print(f"{formatter.pretty(item)}{os.linesep}")
                continue

        print(f"  {item}")

    if len(items) > print_limit:
        remaining = len(items) - print_limit
        print(f"  {remaining} more...")
    print()

    return input('Would you like to insert these into the database [Y/n]? ')
