import csv
import sys
import uuid
import random
import pymysql
import os.path
import argparse
import logging as log

from argparse import RawTextHelpFormatter
from app.db.config import Config
from app.db.database import Database


class OrdersArgParser:
    def __init__(self, args):
        self.parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                              description="""Generate order data in MySQL database.
A comma separated values (CSV) file with a dataset may be provided
as an argument using the --csv option. When this argument is provided,
others will be ignored.

Randomly generated orders will be created if the --csv option is not
used and the --count option is present. There must be existing customers
in the database. The program will exit if there are none.

examples:
    
    python -m app.producers.orders --csv <path-to-csv-file>
    python -m app.producers.orders --count 10 --active 5""")
        self.parser.add_argument('-f', '--csv', type=str, help="""a csv file with order data.
File should be in the format (no header):
orderId,customerId,deliveryId,isActive,confirmationCode""")
        self.parser.add_argument('--count', type=int, help='number of random orders to generate.')
        self.parser.add_argument('--active', type=int, help='how many orders to make active. Default is inactive.')
        self.args = self.parser.parse_args(args)


class Order:
    def __init__(self, order_id, cust_id, deliv_id, is_active, conf_code):
        self.order_id = order_id
        self.cust_id = cust_id
        self.deliv_id = deliv_id
        self.is_active = is_active
        self.conf_code = conf_code

    def __str__(self):
        return f"id: {self.order_id}, custId: {self.cust_id}, delivId: {self.deliv_id}, " \
                f"isActive: {self.is_active}, confCode: {self.conf_code}"


class OrderGenerator:
    @classmethod
    def generate_delivery_id(cls) -> uuid:
        return uuid.uuid4()

    @classmethod
    def generate_order(cls, cust_id, deliv_id, is_active) -> Order:
        order_id = uuid.uuid4()
        conf_code = str(uuid.uuid4())[0:10]
        return Order(order_id, cust_id, deliv_id, is_active, conf_code)


class OrderProducer:
    def __init__(self, db: Database):
        self.db = db

    def save_order(self, order: Order):
        """
        Create a row in the order table.

        :param order: the order to save
        """
        try:
            self.db.open_connection()
            with self.db.conn.cursor() as cursor:
                cursor.execute("INSERT INTO `order` (orderId,customerId,deliveryId,isActive,confirmationCode) "
                               "VALUES (%s, %s, %s, %s, %s)",
                               (order.order_id.bytes, order.cust_id, order.deliv_id, order.is_active, order.conf_code))
                self.db.conn.commit()
        except pymysql.MySQLError as ex:
            print(f"Problem occurred saving order: {order}")
            log.error(ex)
            sys.exit(1)
        finally:
            if self.db.conn:
                self.db.conn = None
                log.info('Database connection closed.')

    def produce_random(self, num_orders: int, cust_ids: list, deliv_ids: list, num_active: int):
        """
        Create random orders. Customer ids will be chosen randomly to create orders.
        By default, orders will be created as not active.

        :param num_orders: the number of order to create
        :param cust_ids: the customer ids to use for orders (not empty)
        :param deliv_ids: the driver ids to use for users (not empty)
        :param num_active: number of active orders. Must be smaller than number of orders.
        """
        if len(cust_ids) == 0 or len(deliv_ids) == 0:
            return

        orders = []
        for _ in range(num_orders):
            is_active = True if num_active > 0 else False
            cust_id = random.choice(cust_ids)
            deliv_id = random.choice(deliv_ids)
            order = OrderGenerator.generate_order(cust_id, deliv_id, is_active)
            orders.append(order)
            num_active -= 1

        print('The following orders will be created:', end=os.linesep * 2)
        print_limit = 10
        for i in range(len(orders)):
            if i >= print_limit:
                break
            print(f"  {orders[i]}")
        if len(orders) > print_limit:
            remaining = len(orders) - print_limit
            print(f"  {remaining} more...")
        print()

        answer = input('Would you like to insert these into the database [Y/n]? ')
        if answer.strip().lower() == 'n':
            print('No records will be inserted.')
            sys.exit(0)
        else:
            for order in orders:
                self.save_order(order)
            print(f"{len(orders)} orders created successfully.")

    def produce_from_csv(self, csv_path: str):
        """
        Create users from a csv file. The csv file should be in the format (no header)
        orderId,customerId,deliveryId,isActive,confirmationCode

        :param csv_path: the path to the csv file
        """
        def to_bytes(uuid_str):
            return uuid.UUID(uuid_str).bytes

        with open(csv_path) as file:
            csv_reader = csv.reader(file, delimiter=',')
            cust_ids = get_customer_ids(self.db)
            deliv_ids = get_delivery_ids(self.db)
            for row in csv_reader:
                cust_id = to_bytes(row[1])
                if cust_id not in cust_ids:
                    print(f"Customer with id {row[1]} does not exist. Order will not be created.")
                    continue
                deliv_id = to_bytes(row[2])
                if deliv_id not in deliv_ids:
                    print(f"Delivery with id {row[2]} does not exist. Order will not be created.")
                    continue
                order_id = uuid.UUID(row[0])
                is_active = bool(row[3])
                conf_code = row[4]
                order = Order(order_id, cust_id, deliv_id, is_active, conf_code)
                self.save_order(order)


def get_customer_ids(db: Database) -> list:
    results = db.run_query("SELECT customerId FROM customer")
    return list(map(lambda result: result[0], results))


def get_delivery_ids(db: Database) -> list:
    results = db.run_query("SELECT deliveryId FROM delivery")
    return list(map(lambda result: result[0], results))


def main(arguments):
    database = Database(Config())
    producer = OrderProducer(database)
    parser = OrdersArgParser(arguments)
    args = parser.args

    if not args.csv and not args.count:
        print('--csv or --count option must be provided.')
        parser.parser.print_help()
        return

    csv_file = args.csv
    if csv_file:
        if not os.path.isfile(csv_file):
            print(f"{csv_file} does not exist.")
            return
        else:
            producer.produce_from_csv(csv_file)
    else:
        count = args.count or 0
        active = args.active or 0
        if count < 1:
            print("A count greater than 0 must be provided.")
            return
        if active > count:
            print('Active orders must be less than or equal to the total count.')
            return

        customer_ids = get_customer_ids(database)
        if len(customer_ids) == 0:
            print('There are no customers in the database. Please add some.')
            return

        delivery_ids = get_delivery_ids(database)
        if len(delivery_ids) == 0:
            print('There are no deliveries in the database. Please add some.')
            return

        producer.produce_random(num_orders=count, cust_ids=customer_ids, deliv_ids=delivery_ids, num_active=active)


if __name__ == '__main__':
    main(sys.argv[1:])
