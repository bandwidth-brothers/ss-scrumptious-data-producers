import os


def print_items_and_confirm(items: list, item_type: str, print_limit: int = 10) -> str:
    """
    Print the items to be inserted into the database (up to a limit)
    abd request for confirmation.

    :param items: the items to be printed
    :param item_type: the type of item that will be created
    :param print_limit: how many items (max) should be printed
    :return: the input from the user
    """
    print(f"The following {item_type} will be created:", end=os.linesep * 2)

    for i in range(len(items)):
        if i >= print_limit:
            break
        print(f"  {items[i]}")
    if len(items) > print_limit:
        remaining = len(items) - print_limit
        print(f"  {remaining} more...")
    print()

    return input('Would you like to insert these into the database [Y/n]? ')
