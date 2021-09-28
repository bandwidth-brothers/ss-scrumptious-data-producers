import os
import sys
import uuid

from app.db.config import Config
from app.db.database import Database
from app.orders.parser import OrdersArgParser
from app.orders.producer import OrderProducer
from app.orders.producer import get_delivery_ids
from app.orders.producer import get_customer_ids
from app.orders.producer import get_restaurant_ids
from app.orders.formatter import OrderFormatter
from app.orders.generator import OrderGenerator
from app.orders.dependencies import OrderDependencies


def main(_args):
    database = Database(Config())
    producer = OrderProducer(database)
    parser = OrdersArgParser(_args)
    args = parser.args

    producer.set_short_output(args.short)
    producer.set_pretty_output(args.pretty)
    producer.set_output_limit(args.limit)

    # run producer program
    if args.command == 'produce':
        if args.deps:
            OrderDependencies.create_dependencies(database, args.deps, args.deps, args.deps)
            return

        if args.delete_all:
            OrderDependencies.delete_all(database)
            return

        count = args.count or 0
        if count < 1:
            print("A count greater than 0 must be provided.")
            return

        customer_ids = get_customer_ids(database)
        if len(customer_ids) == 0:
            print('There are no customers in the database. Please add some.')
            return
        delivery_ids = get_delivery_ids(database)
        if len(delivery_ids) == 0:
            print('There are no deliveries in the database. Please add some.')
            return
        rest_ids = get_restaurant_ids(database)
        if len(rest_ids) == 0:
            print('There are no restaurants in the database. Please add some.')
            return

        producer.produce_random(num_orders=count, cust_ids=customer_ids, deliv_ids=delivery_ids, rest_ids=rest_ids)

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

        order = OrderGenerator.generate_order(cust_id=uuid.uuid4().hex, restaurant_id=5678, deliv_id=91011)
        order.id = 1234

        if args.csv_format:
            print('ID,CUSTOMER_ID,RESTAURANT_ID,DELIVERY_ID,CONFIRMATION_CODE')
            print(OrderFormatter().to_csv([order]))
            print(os.linesep + 'Headers should not be included in the file.')
            return
        if args.json_format:
            print(OrderFormatter().to_json([order]))
            return
        if args.xml_format:
            print(OrderFormatter().to_xml([order]))
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
