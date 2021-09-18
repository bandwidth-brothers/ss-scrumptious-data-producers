
import sys
import uuid
import string
import random
import argparse

from .ids import get_driver_ids
from .ids import get_address_ids
from app.db.config import Config
from app.db.database import Database
from app.producers.users import UserGenerator


def get_last_insert_id(db: Database, table: str, id_name: str):
    db.open_connection()
    with db.conn.cursor() as cursor:
        cursor.execute(f"SELECT MAX({id_name}) FROM `{table}`")
        last_id = cursor.fetchone()[0]
    return last_id if last_id is not None else 1


class AddressData:
    @staticmethod
    def create_addresses(db: Database, count: int):
        address_ids = []
        curr_id = get_last_insert_id(db, 'address', 'addressId')

        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            for _ in range(count):
                line1 = "".join(random.sample(string.ascii_lowercase, 20))
                city = "".join(random.sample(string.ascii_lowercase, 10))
                state = "".join(random.sample(string.ascii_uppercase, 2))
                zipcode = "".join(random.sample(string.digits, 5))
                curr_id += 1
                cursor.execute('INSERT INTO address (addressId,line1,city,state,zip) VALUES (?, ?, ?, ?, ?)',
                               (curr_id, line1, city, state, zipcode))
                address_ids.append(curr_id)
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return address_ids

    @staticmethod
    def delete_addresses(db: Database, address_ids: list):
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            for address_id in address_ids:
                cursor.execute('DELETE FROM address WHERE addressId = ?', (address_id,))
        db.conn.commit()
        db.conn.close()
        db.conn = None


class RestaurantData:
    @classmethod
    def create_restaurants(cls, db: Database, count: int):
        restaurant_and_address_ids = []
        address_ids = AddressData.create_addresses(db, count)
        owner_ids = UserData.create_users(db, count, 'EMPLOYEE')
        curr_id = get_last_insert_id(db, 'restaurant', 'restaurantId')

        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            for i in range(count):
                curr_id += 1
                address_id = address_ids[i]
                restaurant_owner_id = owner_ids[i]
                name = "".join(random.sample(string.ascii_lowercase, 24))
                rating = 5.0
                cursor.execute('INSERT INTO restaurant_owner (restaurantOwnerId) VALUES (UNHEX(?))',
                               (restaurant_owner_id,))
                cursor.execute('INSERT INTO restaurant (restaurantId,addressId,restaurantOwnerId,name,rating) '
                               'VALUES (?, ?, UNHEX(?), ?, ?)',
                               (curr_id, address_id, restaurant_owner_id, name, rating))
                restaurant_and_address_ids.append([curr_id, address_id])
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return [restaurant_and_address_ids, owner_ids]

    @classmethod
    def delete_restaurants(cls, db: Database, ids):
        rest_addr_ids = ids[0]
        owner_ids = ids[2]
        address_ids = []

        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            for rest_addr_id in rest_addr_ids:
                rest_id = rest_addr_id[0]
                address_id = rest_addr_id[1]
                cursor.execute('DELETE FROM restaurant WHERE restaurantId = ? AND addressId = ?', (rest_id, address_id))
                address_ids.append(address_id)
            for owner_id in owner_ids:
                cursor.execute('DELETE FROM restaurant_owner WHERE restaurantOwnerId = UNHEX(?)', (owner_id,))
        db.conn.commit()
        db.conn.close()
        db.conn = None
        AddressData.delete_addresses(db, address_ids)
        UserData.delete_users(db, owner_ids)


class UserData:
    @staticmethod
    def create_users(db: Database, count: int, user_role: str) -> list:
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        user_ids = []
        with db.conn.cursor() as cursor:
            for _ in range(count):
                user_id = uuid.uuid4().hex
                password = UserGenerator.generate_password(password_len=16)
                email = UserGenerator.generate_email(min_len=8, max_len=12)
                cursor.execute('INSERT INTO user (userId,userRole,password,email) '
                               'VALUES (UNHEX(?), ?, ?, ?)',
                               (user_id, user_role, password, email))
                user_ids.append(user_id)
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return user_ids

    @staticmethod
    def delete_users(db: Database, user_ids: list):
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            for user_id in user_ids:
                cursor.execute('DELETE FROM user WHERE userId = UNHEX(?)', (user_id,))
        db.conn.commit()
        db.conn.close()
        db.conn = None


def _get_random_phone_number():
    def _random_digits(num: int):
        return "".join(random.sample(string.digits, num))
    return f"({_random_digits(3)}) {_random_digits(3)}-{_random_digits(4)}"


class CustomerData:
    @staticmethod
    def create_customers(db: Database, count: int) -> list:
        user_ids = UserData.create_users(db, count, 'CUSTOMER')
        customer_ids = []

        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            for i in range(count):
                customer_id = user_ids[i]
                first_name = "".join(random.sample(string.ascii_lowercase, 10))
                last_name = "".join(random.sample(string.ascii_lowercase, 10))
                phone = _get_random_phone_number()
                cursor.execute('INSERT INTO customer (customerId,firstName,lastName,phone) VALUES (UNHEX(?), ?, ?, ?)',
                               (customer_id, first_name, last_name, phone))
                customer_ids.append(customer_id)
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return [customer_ids, user_ids]

    @staticmethod
    def delete_customers(db: Database, customer_user_ids: list):
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            for customer_id in customer_user_ids[0]:
                cursor.execute('DELETE FROM customer WHERE customerId = UNHEX(?)', (customer_id,))
        db.conn.commit()
        db.conn.close()
        db.conn = None
        UserData.delete_users(db, customer_user_ids[1])


class DriverData:
    @staticmethod
    def create_drivers(db: Database, count: int) -> list:
        user_ids = UserData.create_users(db, count, 'DRIVER')
        address_ids = AddressData.create_addresses(db, count)
        driver_ids = []

        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            for i in range(count):
                driver_id = user_ids[i]
                address_id = random.choice(address_ids)
                first_name = "".join(random.sample(string.ascii_lowercase, 10))
                last_name = "".join(random.sample(string.ascii_lowercase, 10))
                phone = _get_random_phone_number()
                licence = random.sample(string.ascii_uppercase, 1)[0] + "".join(random.sample(string.ascii_lowercase, 7))

                cursor.execute('INSERT INTO driver (driverId,addressId,firstName,lastName,phone,licenseNum,status) '
                               'VALUES (UNHEX(?), ?, ?, ?, ?, ?, ?)',
                               (driver_id, address_id, first_name, last_name, phone, licence, 'ACTIVE'))
                driver_ids.append(driver_id)
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return [driver_ids, user_ids]

    @staticmethod
    def delete_drivers(db: Database, driver_user_ids):
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            for driver_id in driver_user_ids[0]:
                cursor.execute('DELETE FROM driver WHERE driverId = UNHEX(?)', (driver_id,))
        db.conn.commit()
        db.conn.close()
        db.conn = None
        UserData.delete_users(db, driver_user_ids[1])


class DeliveryData:
    @staticmethod
    def create_deliveries(db: Database, count: int) -> list:
        driver_ids = get_driver_ids(db)
        address_ids = get_address_ids(db)
        delivery_ids = []
        curr_id = get_last_insert_id(db, 'delivery', 'deliveryId')

        db.open_connection()
        with db.conn.cursor() as cursor:
            for _ in range(count):
                driver_id = random.choice(driver_ids)
                address_id = random.choice(address_ids)
                curr_id += 1
                cursor.execute("INSERT INTO delivery (deliveryId,driverId,destinationId) "
                               "VALUES (?, UNHEX(?), ?)",
                               (curr_id, driver_id, address_id))
                delivery_ids.append(curr_id)
        db.conn.close()
        db.conn = None
        return delivery_ids

    @staticmethod
    def delete_deliveries(db: Database, delivery_ids: list):
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            for delivery_id in delivery_ids:
                cursor.execute('DELETE FROM delivery WHERE deliveryId = ?', (delivery_id,))
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
    parser.add_argument('--restaurants', type=int, help='create restaurants')

    args = parser.parse_args(args)
    db = Database(Config())

    if args.clear:
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            if args.delete_orders:
                cursor.execute('DELETE FROM `order`')
            cursor.execute('DELETE FROM restaurant')
            cursor.execute('DELETE FROM restaurant_owner')
            cursor.execute('DELETE FROM delivery')
            cursor.execute('DELETE FROM driver')
            cursor.execute('DELETE FROM customer')
            cursor.execute('DELETE FROM address')
            cursor.execute('DELETE FROM `user`')
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return

    def create_data(addrs, custs, drivers, delivs, rests):
        AddressData.create_addresses(db, addrs)
        CustomerData.create_customers(db, custs)
        DriverData.create_drivers(db, drivers)
        DeliveryData.create_deliveries(db, delivs)
        RestaurantData.create_restaurants(db, rests)

    if args.all:
        count = args.all
        create_data(addrs=count, custs=count, drivers=count, delivs=count, rests=count)
    else:
        create_data(addrs=args.addresses or 0,
                    custs=args.customers or 0,
                    drivers=args.drivers or 0,
                    delivs=args.deliveries or 0,
                    rests=args.restaurants or 0)


if __name__ == '__main__':
    make_test_data(sys.argv[1:])
