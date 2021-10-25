import argparse

from argparse import RawTextHelpFormatter
from app.common.constants import DEFAULT_OUTPUT_LIMIT


class OrdersArgParser:
    def __init__(self, args):

        self.parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                              description="""Run Order producer or ingestion programs.

Order producer and ingestion programs can be run using either the 'produce'
argument or the 'ingest' argument. To see the help menu for these programs,
append --help to the program name.

examples:

    python -m app.orders ingest --help
    python -m app.orders produce --help""")
        subparsers = self.parser.add_subparsers(help='commands', dest='command')

        produce_parser = subparsers.add_parser('produce', help='run user producer program',
                                               formatter_class=RawTextHelpFormatter,
                                               description="""Generate random order data in MySQL database.

Order data requires relational dependencies: restaurant, customer, and delivery.
If there are none of any of these in the database, an order cannot be created.
Random Order dependencies can be created with the --deps option. When an order
is created, a random restaurant, customer, and delivery will be selected for the order.

Output can be controlled with --pretty, --short, and --limit options.

examples:

    python -m app.orders produce --count 5
    python -m app.orders produce --count 5 --pretty --limit 2
    python -m app.orders produce --deps 5
    python -m app.orders produce --delete-all""")
        produce_parser.add_argument('--count', type=int, metavar='COUNT', help='number of items to create')
        produce_parser.add_argument('--deps', type=int, metavar='COUNT', help='number of each dependency to create')
        produce_parser.add_argument('--delete-all', action='store_true', help='delete all orders and dependencies')
        produce_parser.add_argument('--short', action='store_true', help='print short output for orders')
        produce_parser.add_argument('--pretty', action='store_true', help='print pretty output for orders')
        produce_parser.add_argument('--limit', type=int, help='limit the order creation output. default 10',
                                    default=DEFAULT_OUTPUT_LIMIT)

        ingest_parser = subparsers.add_parser('ingest', help='run user ingestion program',
                                              formatter_class=RawTextHelpFormatter,
                                              description="""Generate order data in MySQL database from data files.

A CSV, JSON, or XML file with a dataset may be provided as an argument using the
--csv, --json, or --xml option, respectively. To see the expected format, use the
--<type>-format option. Files may also be converted from one format to another.

If any items from the files have order ids already in the database, or customer,
restaurant, delivery ids not in the database, the order will not be created.

Output can be controlled with --pretty, --short, and --limit options.

examples:

    python -m app.orders ingest --csv orders.csv --short --limit 5
    python -m app.orders ingest --json orders.json --short
    python -m app.orders ingest --xml orders.xml --pretty
    python -m app.orders ingest --json-format
    python -m app.orders ingest --convert orders.csv orders.json""")
        ingest_parser.add_argument('--csv', type=str, help='a CSV file with order data.')
        ingest_parser.add_argument('--csv-format', action='store_true', help='show CSV format')
        ingest_parser.add_argument('--json', type=str, help='a JSON file with order data.')
        ingest_parser.add_argument('--json-format', action='store_true', help='show the JSON format')
        ingest_parser.add_argument('--xml', type=str, help='an XML file with order data.')
        ingest_parser.add_argument('--xml-format', action='store_true', help='show the XML format')
        ingest_parser.add_argument('--convert', nargs=2, metavar=('FROM', 'TO'), type=str,
                                   help='convert one file format to another.')
        ingest_parser.add_argument('--short', action='store_true', help='print short output for orders')
        ingest_parser.add_argument('--pretty', action='store_true', help='print pretty output for orders')
        ingest_parser.add_argument('--limit', type=int, help='limit the order creation output. default 10',
                                   default=DEFAULT_OUTPUT_LIMIT)

        self.args = self.parser.parse_args(args)
