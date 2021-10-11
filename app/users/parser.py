import argparse

from argparse import RawTextHelpFormatter
from app.common.constants import DEFAULT_OUTPUT_LIMIT


class UsersArgParser:
    def __init__(self, args):
        self.parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                              description="""Run User producer or ingestion programs.

User producer and ingestion programs can be run using either the 'produce'
argument or the 'ingest' argument. To see the help menu for these programs,
append --help to the program name.

examples:

    python -m app.users ingest --help
    python -m app.users produce --help""")
        subparsers = self.parser.add_subparsers(help='commands', dest='command')

        produce_parser = subparsers.add_parser('produce', help='run user producer program',
                                               formatter_class=RawTextHelpFormatter,
                                               description="""Generate random user data in MySQL database.

Users can be created based on their role. The number of users for each role
can be controlled with with provided options. Output can be controlled with
--pretty, --short, and --limit options.

examples:

    python -m app.users produce --all 5
    python -m app.users produce --custs 20 --admins 2 --emps 5 --drivers 5
    python -m app.users produce --custs 20 --pretty --limit 5
    python -m app.users produce --admins 2""")
        produce_parser.add_argument('--all', type=int, metavar='COUNT', help='number of each type of user to create')
        produce_parser.add_argument('--custs', type=int, metavar='COUNT', help='number of customers to generate')
        produce_parser.add_argument('--admins', type=int, metavar='COUNT', help='number of admins to generate')
        produce_parser.add_argument('--emps', type=int, metavar='COUNT', help='number of employees to generate')
        produce_parser.add_argument('--drivers', type=int, metavar='COUNT', help='number of drivers to generate')
        produce_parser.add_argument('--short', action='store_true', help='print short output for users')
        produce_parser.add_argument('--pretty', action='store_true', help='print pretty output for users')
        produce_parser.add_argument('--limit', type=int, help='limit the user creation output. default 10',
                                    default=DEFAULT_OUTPUT_LIMIT)

        ingest_parser = subparsers.add_parser('ingest', help='run user ingestion program',
                                              formatter_class=RawTextHelpFormatter,
                                              description="""Generate user data in MySQL database from data files.

A CSV, JSON, or XML file with a dataset may be provided as an argument using the
--csv, --json, or --xml option, respectively. To see the expected format, use the
--<type>-format option. Files may also be converted from one format to another.
Output can be controlled with --pretty, --short, and --limit options.

examples:

    python -m app.users ingest --csv users.csv --short --limit 5
    python -m app.users ingest --json users.json --short
    python -m app.users ingest --xml users.xml --pretty
    python -m app.users ingest --json-format
    python -m app.users ingest --convert users.csv users.json""")
        ingest_parser.add_argument('--csv', type=str, help='a CSV file with user data.')
        ingest_parser.add_argument('--csv-format', action='store_true', help='show CSV format')
        ingest_parser.add_argument('--json', type=str, help='a JSON file with user data.')
        ingest_parser.add_argument('--json-format', action='store_true', help='show the JSON format')
        ingest_parser.add_argument('--xml', type=str, help='an XML file with user data.')
        ingest_parser.add_argument('--xml-format', action='store_true', help='show the XML format')
        ingest_parser.add_argument('--convert', nargs=2, metavar=('FROM', 'TO'), type=str,
                                   help='convert one file format to another.')
        ingest_parser.add_argument('--short', action='store_true', help='print short output for users')
        ingest_parser.add_argument('--pretty', action='store_true', help='print pretty output for users')
        ingest_parser.add_argument('--limit', type=int, help='limit the user creation output. default 10',
                                   default=DEFAULT_OUTPUT_LIMIT)

        self.args = self.parser.parse_args(args)
