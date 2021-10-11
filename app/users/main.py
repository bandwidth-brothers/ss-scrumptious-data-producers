import os
import sys

from app.db.config import Config
from app.db.database import Database
from app.users.model import User
from app.users.producer import UsersProducer
from app.users.formatter import UserFormatter
from app.users.generator import UserGenerator
from app.users.parser import UsersArgParser


def main(_args):
    producer = UsersProducer(Database(Config()))
    parser = UsersArgParser(_args)
    args = parser.args

    producer.set_short_output(args.short)
    producer.set_pretty_output(args.pretty)
    producer.set_output_limit(args.limit)

    # run producer program
    if args.command == 'produce':
        if args.all:
            count = args.all
            producer.produce_random(num_custs=count, num_admins=count, num_emps=count, num_drivers=count)
        else:
            custs = args.custs or 0
            admins = args.admins or 0
            emps = args.emps or 0
            drivers = args.drivers or 0
            producer.produce_random(num_custs=custs, num_admins=admins, num_emps=emps, num_drivers=drivers)
        return

    # run ingestor program
    elif args.command == 'ingest':
        def _check_file(file):
            if not os.path.isfile(file):
                print(f"{file} does not exist.")
                sys.exit(1)

        if args.convert:
            _check_file(args.convert[0])
            producer.convert_files(in_file=args.convert[0], out_file=args.convert[1])
            return

        if args.csv_format:
            print('ID,USER_ROLE,PASSWORD,EMAIL,ENABLED,CONFIRMED,ACCT_EXPIRED,ACCT_LOCKED,CRED_EXPIRED')
            print(UserFormatter().to_csv([UserGenerator.generate_user(User.Role.ADMIN)]))
            print(os.linesep + 'Headers should not be included in the file.')
            return

        if args.json_format:
            print(UserFormatter().to_json([UserGenerator.generate_user(User.Role.ADMIN)]))
            return

        if args.xml_format:
            print(UserFormatter().to_xml([UserGenerator.generate_user(User.Role.ADMIN)]))
            return

        def _produce_from_file(file, _produce_func):
            _check_file(file)
            _produce_func(file)

        if args.csv:
            _produce_from_file(args.csv, producer.produce_from_csv)
        elif args.json:
            _produce_from_file(args.json, producer.produce_from_json)
        elif args.xml:
            _produce_from_file(args.xml, producer.produce_from_xml)
