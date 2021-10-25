import sys
import json
import random
import pymysql
import logging as log
import xml.etree.ElementTree

from typing import Type
from app.db.database import Database
from app.orders.model import Order
from app.orders.formatter import OrderFormatter
from app.orders.generator import OrderGenerator
from app.common.producer import AbstractProducer
from app.common.constants import DEFAULT_OUTPUT_LIMIT
from app.common.exceptions import MissingAttributeException


class OrderProducer(AbstractProducer[Order]):
    def __init__(self, db: Database):
        super(OrderProducer, self).__init__(db)
        self.output_limit = DEFAULT_OUTPUT_LIMIT
        self._cust_ids = get_customer_ids(self.db)
        self._deliv_ids = get_delivery_ids(self.db)
        self._order_ids = get_order_ids(self.db)
        self._rest_ids = get_restaurant_ids(self.db)

    def save(self, order: Order):
        return self.save_order(order)

    def save_order(self, order: Order):
        """
        Create a row in the order table.

        :param order: the order to save
        """
        try:
            self.db.open_connection()
            with self.db.conn.cursor() as cursor:
                if order.id is None:
                    cursor.execute(
                        "INSERT INTO `order` (customer_id,restaurant_id,delivery_id,confirmation_code) "
                        "VALUES (UNHEX(?), ?, ?, ?)",
                        (order.customer_id, order.restaurant_id, order.delivery_id, order.confirmation_code))
                else:
                    cursor.execute(
                        "INSERT INTO `order` "
                        "(id,customer_id,restaurant_id,delivery_id,confirmation_code) "
                        "VALUES (?, UNHEX(?), ?, ?, ?)",
                        (order.id, order.customer_id, order.restaurant_id, order.delivery_id, order.confirmation_code))
            return True
        except pymysql.MySQLError as ex:
            print(f"Problem occurred saving order: {order}")
            log.error(ex)
            return False
        finally:
            if self.db.conn:
                self.db.conn = None
                log.info('Database connection closed.')

    def produce_random(self, num_orders: int, cust_ids: list, deliv_ids: list, rest_ids: list):
        """
        Create random items. Customer ids will be chosen randomly to create items.
        By default, items will be created as not active.

        :param num_orders: the number of items to create
        :param cust_ids: the customer ids to use for items (not empty)
        :param deliv_ids: the driver ids to use for users (not empty)
        :param rest_ids: a list of lists of restaurant and address ids.
        """
        if len(cust_ids) == 0 or len(deliv_ids) == 0 or rest_ids == 0:
            return

        orders = []
        for _ in range(num_orders):
            cust_id = random.choice(cust_ids)
            rest_id = random.choice(rest_ids)
            deliv_id = random.choice(deliv_ids)
            order = OrderGenerator.generate_order(cust_id=cust_id, restaurant_id=rest_id, deliv_id=deliv_id)
            orders.append(order)

        self._confirm_and_save(orders)

    def produce_from_csv(self, csv_path: str):
        """
        Create users from a csv file. The csv file should be in the format (no header)
        id,customer_id,restaurant_id,delivery_id,confirmation_code

        :param csv_path: the path to the csv file
        """
        orders = []
        with open(csv_path) as file:
            try:
                _orders = OrderFormatter().from_csv(file.read())
            except IndexError:
                print(f"There are missing fields. Rows must contain all properties.")
                _orders = []

            for order in _orders:
                if not self._validate_order(order):
                    print("Order will not be created.")
                else:
                    orders.append(order)

        self._confirm_and_save(orders)

    def produce_from_json(self, json_file):
        """
        Create users from a json file. All fields are required.

        :param json_file: the path to the json file
        """
        orders = []
        with open(json_file) as f:
            try:
                _orders = OrderFormatter().from_json(f.read())
            except json.decoder.JSONDecodeError:
                print('JSON is not valid format.')
                sys.exit(1)
            except MissingAttributeException as k_ex:
                print(f"Order missing {k_ex}. All fields are required.")
                sys.exit(1)
            except ValueError as v_ex:
                print(v_ex)
                sys.exit(1)

        for order in _orders:
            if not self._validate_order(order):
                print("Order will not be created.")
            else:
                orders.append(order)

        self._confirm_and_save(orders)

    def produce_from_xml(self, xml_file):
        """
        Create items from an xml file. All fields must be present.

        :param xml_file: the path to the xml file
        """
        orders = []
        with open(xml_file) as f:
            try:
                _orders = OrderFormatter().from_xml(f.read())
            except xml.etree.ElementTree.ParseError as p_ex:
                print(f"Malformed XML: {p_ex}")
                sys.exit(1)
            except KeyError as k_ex:
                print(f"Order missing {k_ex}. All fields are required.")
                sys.exit(1)

        for order in _orders:
            if not self._validate_order(order):
                print("Order will not be created.")
            else:
                orders.append(order)

        self._confirm_and_save(orders)

    def _validate_order(self, order: Order) -> bool:
        """
        Validate order to make sure it contains valid referential ids.
        Orders require a customer_id, restaurant_id, and delivery_id
        that are all in the database already.

        :param order: the Order to validate.
        :return: True if the order is valid or False if it is not
        """
        if order.id in self._order_ids:
            print(f"Order with id {order.id} already exists.")
            return False
        if order.customer_id not in self._cust_ids:
            print(f"Customer with id {order.customer_id} does not exist.")
            return False
        if order.restaurant_id not in self._rest_ids:
            print(f"Restaurant with id {order.restaurant_id} does not exist.")
            return False
        if order.delivery_id not in self._deliv_ids:
            print(f"Delivery with id {order.delivery_id} does not exist.")
            return False
        return True

    def get_formatter(self) -> OrderFormatter:
        return OrderFormatter()

    def get_object_type(self) -> Type[Order]:
        return Order


def _get_ids(db: Database, sql: str) -> list:
    results = db.run_query(sql)
    return list(map(lambda result: result[0], results))


def get_order_ids(db: Database) -> list:
    return _get_ids(db, "SELECT id FROM `order`")


def get_customer_ids(db: Database) -> list:
    return list(map(lambda _id: _id.lower(), _get_ids(db, "SELECT HEX(id) FROM customer")))


def get_delivery_ids(db: Database) -> list:
    return _get_ids(db, "SELECT id FROM delivery")


def get_restaurant_ids(db: Database) -> list:
    return _get_ids(db, "SELECT id FROM restaurant")
