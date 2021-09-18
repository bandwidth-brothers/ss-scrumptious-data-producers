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
from app.producers.helpers import print_items_and_confirm


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
        self.args = self.parser.parse_args(args)


class Order:
    def __init__(self, order_id, cust_id: str, deliv_id: int,
                 restaurant_id: int, restaurant_address_id: int, conf_code: str):
        """
        Constructor for creating an Order.

        :param order_id: int id of order
        :param cust_id: Hex string of UUID
        :param deliv_id: int id of delivery
        :param restaurant_id: int id of restaurant
        :param restaurant_address_id int id of restaurant address
        :param conf_code: string confirmation code
        """
        self.order_id = order_id
        self.cust_id = cust_id
        self.restaurant_id = restaurant_id
        self.restaurant_address_id = restaurant_address_id
        self.deliv_id = deliv_id
        self.conf_code = conf_code

    def __str__(self):
        return f"orderId: {self.order_id}, custId: {self.cust_id}, restaurantId: {self.restaurant_id}, " \
               f"restaurantAddressId: {self.restaurant_address_id}, delivId: {self.deliv_id}, " \
               f"confCode: {self.conf_code}"


class OrderGenerator:
    @classmethod
    def generate_order(cls, cust_id: str, deliv_id: int, restaurant_id: int, restaurant_address_id: int) -> Order:
        """
        Generate an Order object.

        :param cust_id: a uuid hex string of customer id
        :param deliv_id: a uuid hex string of deliver id
        :param restaurant_id: int id of restaurant
        :param restaurant_address_id int id or restaurant address
        :return: the Order
        """
        conf_code = str(uuid.uuid4()).replace('-', '')[0:10]
        return Order(order_id=None, cust_id=cust_id, deliv_id=deliv_id, restaurant_id=restaurant_id,
                     restaurant_address_id=restaurant_address_id, conf_code=conf_code)


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
                if order.order_id is None:
                    cursor.execute(
                        "INSERT INTO `order` "
                        "(customerId,deliveryId,restaurantId,restaurantAddressId,confirmationCode) "
                        "VALUES (UNHEX(?), ?, ?, ?, ?)",
                        (order.cust_id, order.deliv_id, order.restaurant_id, order.restaurant_address_id, order.conf_code))
                else:
                    cursor.execute(
                        "INSERT INTO `order` "
                        "(orderId,customerId,deliveryId,restaurantId,restaurantAddressId,confirmationCode) "
                        "VALUES (?, UNHEX(?), ?, ?, ?, ?)",
                        (order.order_id, order.cust_id, order.deliv_id, order.restaurant_id,
                         order.restaurant_address_id, order.conf_code))
        except pymysql.MySQLError as ex:
            print(f"Problem occurred saving order: {order}")
            log.error(ex)
            sys.exit(1)
        finally:
            if self.db.conn:
                self.db.conn = None
                log.info('Database connection closed.')

    def produce_random(self, num_orders: int, cust_ids: list, deliv_ids: list, rest_addr_ids: list):
        """
        Create random orders. Customer ids will be chosen randomly to create orders.
        By default, orders will be created as not active.

        :param num_orders: the number of orders to create
        :param cust_ids: the customer ids to use for orders (not empty)
        :param deliv_ids: the driver ids to use for users (not empty)
        :param rest_addr_ids: a list of lists of restaurant and address ids.
        """
        if len(cust_ids) == 0 or len(deliv_ids) == 0 or rest_addr_ids == 0:
            return

        orders = []
        for _ in range(num_orders):
            cust_id = random.choice(cust_ids)
            deliv_id = random.choice(deliv_ids)
            rest_addr_id = random.choice(rest_addr_ids)
            order = OrderGenerator.generate_order(cust_id, deliv_id, rest_addr_id[0], rest_addr_id[1])
            orders.append(order)

        answer = print_items_and_confirm(items=orders, item_type='orders')
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
        orderId,customerId,deliveryId,restaurantId,restaurantAddressId,confirmationCode

        :param csv_path: the path to the csv file
        """
        with open(csv_path) as file:
            csv_reader = csv.reader(file, delimiter=',')
            cust_ids = get_customer_ids(self.db)
            deliv_ids = get_delivery_ids(self.db)
            order_ids = get_order_ids(self.db)
            rest_addr_ids = get_restaurant_and_address_ids(self.db)
            for row in csv_reader:
                order_id = int(row[0])
                if order_id in order_ids:
                    print(f"Order with id {order_id} already exists. Order will not be created.")
                    continue
                cust_id = row[1].lower()
                if cust_id not in cust_ids:
                    print(f"Customer with id {cust_id} does not exist. Order will not be created.")
                    continue
                deliv_id = int(row[2])
                if deliv_id not in deliv_ids:
                    print(f"Delivery with id {deliv_id} does not exist. Order will not be created.")
                    continue
                restaurant_id = int(row[3])
                address_id = int(row[4])
                if (restaurant_id, address_id) not in rest_addr_ids:
                    print(f"Restaurant with restaurantId {restaurant_id} and addressId {address_id} does not exist. "
                          f"Order will not be created.")
                    continue
                conf_code = row[5]
                order = Order(order_id=order_id, cust_id=cust_id, deliv_id=deliv_id, restaurant_id=restaurant_id,
                              restaurant_address_id=address_id, conf_code=conf_code)
                self.save_order(order)


def get_order_ids(db: Database) -> list:
    results = db.run_query("SELECT orderId FROM `order`")
    return list(map(lambda result: result[0], results))


def get_customer_ids(db: Database) -> list:
    results = db.run_query("SELECT HEX(customerId) FROM customer")
    return list(map(lambda result: result[0].lower(), results))


def get_delivery_ids(db: Database) -> list:
    results = db.run_query("SELECT deliveryId FROM delivery")
    return list(map(lambda result: result[0], results))


def get_restaurant_and_address_ids(db: Database) -> list[tuple]:
    return db.run_query("SELECT restaurantId,addressId FROM restaurant")


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

        restaurant_and_address_ids = get_restaurant_and_address_ids(database)
        if len(restaurant_and_address_ids) == 0:
            print('There are no restaurants in the database. Please add some.')
            return

        producer.produce_random(num_orders=count, cust_ids=customer_ids, deliv_ids=delivery_ids,
                                rest_addr_ids=restaurant_and_address_ids)


if __name__ == '__main__':
    main(sys.argv[1:])
