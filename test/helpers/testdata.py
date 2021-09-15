
import sys
import uuid
import string
import random
import argparse

from .ids import get_user_ids
from .ids import get_driver_ids
from .ids import get_address_ids
from app.db.config import Config
from app.db.database import Database


class AddressData:
    @staticmethod
    def create_addresses(db: Database, count: int):
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        address_ids = []
        for _ in range(count):
            address_id = uuid.uuid4().hex
            line1 = "".join(random.sample(string.ascii_lowercase, 20))
            city = "".join(random.sample(string.ascii_lowercase, 10))
            state = "".join(random.sample(string.ascii_uppercase, 10))
            zipcode = "".join(random.sample(string.digits, 5))
            with db.conn.cursor() as cursor:
                cursor.execute('INSERT INTO address (addressId,line1,city,state,zip) VALUES (UNHEX(?), ?, ?, ?, ?)',
                               (address_id, line1, city, state, zipcode))
            address_ids.append(address_id)
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return address_ids

    @staticmethod
    def delete_addresses(db: Database, address_ids: list):
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        for address_id in address_ids:
            with db.conn.cursor() as cursor:
                cursor.execute('DELETE FROM address WHERE addressId = UNHEX(?)', (address_id,))
        db.conn.commit()
        db.conn.close()
        db.conn = None


class UserData:
    @staticmethod
    def create_users(db: Database, count: int, user_role: str) -> list:
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        user_ids = []
        for _ in range(count):
            user_id = uuid.uuid4().hex
            username = "".join(random.sample(string.ascii_lowercase, 10))
            password = "".join(random.sample(string.ascii_lowercase, 10))
            email = "".join(random.sample(string.ascii_uppercase, 10))
            with db.conn.cursor() as cursor:
                cursor.execute('INSERT INTO user (userId,userRole,username,password,email) '
                               'VALUES (UNHEX(?), ?, ?, ?, ?)',
                               (user_id, user_role, username, password, email))
            user_ids.append(user_id)
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return user_ids

    @staticmethod
    def delete_users(db: Database, user_ids: list):
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        for user_id in user_ids:
            with db.conn.cursor() as cursor:
                cursor.execute('DELETE FROM user WHERE userId = UNHEX(?)', (user_id,))
        db.conn.commit()
        db.conn.close()
        db.conn = None


class CustomerData:
    @staticmethod
    def create_customers(db: Database, count: int) -> list:
        user_ids = get_user_ids(db, 'CUSTOMER')
        customer_ids = []
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        for _ in range(count):
            customer_id = uuid.uuid4().hex
            user_id = random.choice(user_ids)
            with db.conn.cursor() as cursor:
                cursor.execute('INSERT INTO customer (customerId,userId) VALUES (UNHEX(?), UNHEX(?))',
                               (customer_id, user_id))
            customer_ids.append(customer_id)
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return customer_ids

    @staticmethod
    def delete_customers(db: Database, customer_ids: list):
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        for customer_id in customer_ids:
            with db.conn.cursor() as cursor:
                cursor.execute('DELETE FROM customer WHERE customerId = UNHEX(?)', (customer_id,))
        db.conn.commit()
        db.conn.close()
        db.conn = None


class DriverData:
    @staticmethod
    def create_drivers(db: Database, count: int) -> list:
        user_ids = get_user_ids(db, 'DRIVER')
        address_ids = get_address_ids(db)
        driver_ids = []
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        for _ in range(count):
            driver_id = uuid.uuid4().hex
            user_id = random.choice(user_ids)
            address_id = random.choice(address_ids)
            with db.conn.cursor() as cursor:
                cursor.execute('INSERT INTO driver (driverId,userId,locationId) VALUES (UNHEX(?), UNHEX(?), UNHEX(?))',
                               (driver_id, user_id, address_id))
            driver_ids.append(driver_id)
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return driver_ids

    @staticmethod
    def delete_drivers(db: Database, driver_ids):
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        for driver_id in driver_ids:
            with db.conn.cursor() as cursor:
                cursor.execute('DELETE FROM driver WHERE driverId = UNHEX(?)', (driver_id,))
        db.conn.commit()
        db.conn.close()
        db.conn = None


class DeliveryData:
    @staticmethod
    def create_deliveries(db: Database, count: int) -> list:
        driver_ids = get_driver_ids(db)
        address_ids = get_address_ids(db)
        delivery_ids = []
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        for _ in range(count):
            delivery_id = uuid.uuid4().hex
            driver_id = random.choice(driver_ids)
            address_id = random.choice(address_ids)
            with db.conn.cursor() as cursor:
                cursor.execute("INSERT INTO delivery (deliveryId,driverId,destinationId) "
                               "VALUES (UNHEX(?), UNHEX(?), UNHEX(?))",
                               (delivery_id, driver_id, address_id))
            delivery_ids.append(delivery_id)
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return delivery_ids

    @staticmethod
    def delete_deliveries(db: Database, delivery_ids: list):
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        for delivery_id in delivery_ids:
            with db.conn.cursor() as cursor:
                cursor.execute('DELETE FROM delivery WHERE deliveryId = UNHEX(?)', (delivery_id,))
        db.conn.commit()
        db.conn.close()
        db.conn = None


def make_test_data(args):
    parser = argparse.ArgumentParser(description='Create test data')
    parser.add_argument('--clear', action='store_true', help='clear all records')
    parser.add_argument('--delete-orders', action='store_true', help='delete orders when --clear is used')
    parser.add_argument('--all', type=int, help='create n of each type')
    parser.add_argument('--addresses', type=int, help='create addresses')
    parser.add_argument('--customers', type=int, help='create customers')
    parser.add_argument('--drivers', type=int, help='create drivers')
    parser.add_argument('--deliveries', type=int, help='create deliveries')

    args = parser.parse_args(args)
    db = Database(Config())

    if args.clear:
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            if args.delete_orders:
                cursor.execute('DELETE FROM `order`')
            cursor.execute('DELETE FROM delivery')
            cursor.execute('DELETE FROM driver')
            cursor.execute('DELETE FROM customer')
            cursor.execute('DELETE FROM address')
            cursor.execute('DELETE FROM `user`')
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return

    def create_date(addrs, custs, drivers, delivs):
        AddressData.create_addresses(db, addrs)
        UserData.create_users(db, 5, 'CUSTOMER')
        UserData.create_users(db, 5, 'DRIVER')
        CustomerData.create_customers(db, custs)
        DriverData.create_drivers(db, drivers)
        DeliveryData.create_deliveries(db, delivs)

    if args.all:
        count = args.all
        create_date(addrs=count, custs=count, drivers=count, delivs=count)
    else:
        create_date(addrs=args.addresses or 0,
                    custs=args.customers or 0,
                    drivers=args.drivers or 0,
                    delivs=args.deliveries or 0)


if __name__ == '__main__':
    make_test_data(sys.argv[1:])
