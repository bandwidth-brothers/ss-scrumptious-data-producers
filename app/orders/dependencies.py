import os
import uuid
import string
import random

from app.db.database import Database
from app.producers.users import UserGenerator


class GeneratedIds:
    def __init__(self, addr_ids=None, user_ids=None, rest_ids=None, cust_ids=None, driver_ids=None, deliv_ids=None):

        def _init_ids(ids):
            return [] if ids is None else ids

        self.deliv_ids = _init_ids(deliv_ids)
        self.driver_ids = _init_ids(driver_ids)
        self.cust_ids = _init_ids(cust_ids)
        self.addr_ids = _init_ids(addr_ids)
        self.rest_ids = _init_ids(rest_ids)
        self.user_ids = _init_ids(user_ids)


def get_last_insert_id(db: Database, table: str):
    db.open_connection()
    with db.conn.cursor() as cursor:
        cursor.execute(f"SELECT MAX(id) FROM `{table}`")
        last_id = cursor.fetchone()[0]
    return last_id if last_id is not None else 1


class OrderDependencies:
    @staticmethod
    def create_dependencies(db: Database, num_custs: int, num_rests: int, num_delivs: int):
        for _ in range(num_custs):
            CustomerData.create_customers(db, num_custs)
        print(f"{num_custs} customers created.")
        for _ in range(num_rests):
            RestaurantData.create_restaurants(db, num_rests)
        print(f"{num_rests} restaurants created.")
        for _ in range(num_delivs):
            DeliveryData.create_deliveries(db, num_delivs)
        print(f"{num_delivs} deliveries created.")

    @staticmethod
    def delete_all(db: Database):
        db.open_connection()
        with db.conn.cursor() as curs:
            sql = """
            SELECT COUNT(delivery.id), COUNT(`order`.id), COUNT(driver.id), 
                   COUNT(restaurant.id), COUNT(a1.id), COUNT(a2.id) 
            FROM `order` JOIN restaurant ON `order`.restaurant_id = restaurant.id
            JOIN address a1 ON a1.id = restaurant.address_id
            JOIN delivery ON delivery.id = `order`.delivery_id
            JOIN driver ON driver.id = delivery.driver_id
            JOIN address a2 on driver.address_id = a2.id
            """
            curs.execute(sql)
            counts = curs.fetchone()
        db.conn.close()
        db.conn = None

        delivs = counts[0]
        orders = counts[1]
        drivers = counts[2]
        rests = counts[3]
        addrs = counts[4] + counts[5]

        prompt = f"{orders} orders,{os.linesep}" \
                 f"{rests} restaurants,{os.linesep}" \
                 f"{drivers} drivers,{os.linesep}" \
                 f"{delivs} deliveries,{os.linesep}" \
                 f"{addrs} address will be deleted.{os.linesep}" \
                 f"Would you like to continue [y/N]? "
        answer = input(prompt)

        if answer.strip().lower() == 'y':
            db.open_connection()
            db.conn.jconn.setAutoCommit(False)
            with db.conn.cursor() as cursor:
                cursor.execute('DELETE FROM `order`')
                cursor.execute('DELETE FROM restaurant')
                cursor.execute('DELETE FROM owner')
                cursor.execute('DELETE FROM delivery')
                cursor.execute('DELETE FROM driver')
                cursor.execute('DELETE FROM customer')
                cursor.execute('DELETE FROM address')
                cursor.execute('DELETE FROM `user`')
            db.conn.commit()
            db.conn.close()
            db.conn = None
            print('All records deleted.')
        else:
            print("No records will be deleted.")


class AddressData:
    @staticmethod
    def create_addresses(db: Database, count: int):
        address_ids = []
        curr_id = get_last_insert_id(db, 'address')

        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            for _ in range(count):
                line1 = "".join(random.sample(string.ascii_lowercase, 20))
                city = "".join(random.sample(string.ascii_lowercase, 10))
                state = "".join(random.sample(string.ascii_uppercase, 2))
                zipcode = "".join(random.sample(string.digits, 5))
                curr_id += 1
                cursor.execute('INSERT INTO address (id,line1,city,state,zip) VALUES (?, ?, ?, ?, ?)',
                               (curr_id, line1, city, state, zipcode))
                address_ids.append(curr_id)
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return GeneratedIds(addr_ids=address_ids)

    # @staticmethod
    # def delete_addresses(db: Database, ids: GeneratedIds):
    #     db.open_connection()
    #     db.conn.jconn.setAutoCommit(False)
    #     with db.conn.cursor() as cursor:
    #         for address_id in ids.addr_ids:
    #             cursor.execute('DELETE FROM address WHERE id = ?', (address_id,))
    #     db.conn.commit()
    #     db.conn.close()
    #     db.conn = None


class RestaurantData:
    @staticmethod
    def create_restaurants(db: Database, count: int):
        address_ids = AddressData.create_addresses(db, count).addr_ids
        owner_ids = UserData.create_users(db, count, 'EMPLOYEE').user_ids
        restaurant_ids = []
        curr_id = get_last_insert_id(db, 'restaurant')

        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            for i in range(count):
                curr_id += 1
                address_id = address_ids[i]
                owner_id = owner_ids[i]
                name = "".join(random.sample(string.ascii_lowercase, 24))
                rating = 5.0
                cursor.execute('INSERT INTO owner (id) VALUES (UNHEX(?))',
                               (owner_id,))
                cursor.execute('INSERT INTO restaurant (id, address_id, owner_id, name, rating) '
                               'VALUES (?, ?, UNHEX(?), ?, ?)',
                               (curr_id, address_id, owner_id, name, rating))
                restaurant_ids.append([curr_id, address_id])
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return GeneratedIds(rest_ids=restaurant_ids, addr_ids=address_ids, user_ids=owner_ids)

    # @staticmethod
    # def delete_restaurants(db: Database, ids: GeneratedIds):
    #     db.open_connection()
    #     db.conn.jconn.setAutoCommit(False)
    #     with db.conn.cursor() as cursor:
    #         for rest_id in ids.rest_ids:
    #             cursor.execute('DELETE FROM restaurant WHERE id = ?', (rest_id,))
    #         for owner_id in ids.user_ids:
    #             cursor.execute('DELETE FROM owner WHERE id = UNHEX(?)', (owner_id,))
    #     db.conn.commit()
    #     db.conn.close()
    #     db.conn = None
    #
    #     AddressData.delete_addresses(db, ids)
    #     UserData.delete_users(db, ids)


class UserData:
    @staticmethod
    def create_users(db: Database, count: int, user_role: str) -> GeneratedIds:
        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        user_ids = []
        with db.conn.cursor() as cursor:
            for _ in range(count):
                user_id = uuid.uuid4().hex
                user = UserGenerator.generate_user(user_role)
                user.id = user_id
                cursor.execute('INSERT INTO user (id,user_role,password,email,enabled,confirmed,account_non_expired,'
                               'account_non_locked,credentials_non_expired) VALUES (UNHEX(?), ?, ?, ?, ?, ?, ?, ?, ?)',
                               (user.id, user.user_role, user.password, user.email, user.enabled, user.confirmed,
                                user.account_non_expired, user.account_non_locked, user.credentials_non_expired))
                user_ids.append(user_id)
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return GeneratedIds(user_ids=user_ids)

    # @staticmethod
    # def delete_users(db: Database, ids: GeneratedIds):
    #     db.open_connection()
    #     db.conn.jconn.setAutoCommit(False)
    #     with db.conn.cursor() as cursor:
    #         for user_id in ids.user_ids:
    #             cursor.execute('DELETE FROM user WHERE id = UNHEX(?)', (user_id,))
    #     db.conn.commit()
    #     db.conn.close()
    #     db.conn = None


def _get_random_phone_number():
    def _random_digits(num: int):
        return "".join(random.sample(string.digits, num))
    return f"({_random_digits(3)}) {_random_digits(3)}-{_random_digits(4)}"


class CustomerData:
    @staticmethod
    def create_customers(db: Database, count: int) -> GeneratedIds:
        cust_ids = UserData.create_users(db, count, 'CUSTOMER').user_ids

        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            for cust_id in cust_ids:
                first_name = "".join(random.sample(string.ascii_lowercase, 10))
                last_name = "".join(random.sample(string.ascii_lowercase, 10))
                phone = _get_random_phone_number()
                cursor.execute('INSERT INTO customer (id,first_name,last_name,phone) VALUES (UNHEX(?), ?, ?, ?)',
                               (cust_id, first_name, last_name, phone))
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return GeneratedIds(user_ids=cust_ids)

    # @staticmethod
    # def delete_customers(db: Database, ids: GeneratedIds):
    #     db.open_connection()
    #     db.conn.jconn.setAutoCommit(False)
    #     with db.conn.cursor() as cursor:
    #         for customer_id in ids.user_ids:
    #             cursor.execute('DELETE FROM customer WHERE id = UNHEX(?)', (customer_id,))
    #     db.conn.commit()
    #     db.conn.close()
    #     db.conn = None
    #
    #     UserData.delete_users(db, ids)


class DriverData:
    @staticmethod
    def create_drivers(db: Database, count: int) -> GeneratedIds:
        driver_ids = UserData.create_users(db, count, 'DRIVER').user_ids
        addr_ids = AddressData.create_addresses(db, count).addr_ids

        db.open_connection()
        db.conn.jconn.setAutoCommit(False)
        with db.conn.cursor() as cursor:
            for driver_id in driver_ids:
                address_id = random.choice(addr_ids)
                first_name = "".join(random.sample(string.ascii_lowercase, 10))
                last_name = "".join(random.sample(string.ascii_lowercase, 10))
                phone = _get_random_phone_number()
                licence = random.sample(string.ascii_uppercase, 1)[0] + "".join(random.sample(string.ascii_lowercase, 7))
                cursor.execute('INSERT INTO driver (id,address_id,first_name,last_name,phone,license_num,status) '
                               'VALUES (UNHEX(?), ?, ?, ?, ?, ?, ?)',
                               (driver_id, address_id, first_name, last_name, phone, licence, 'ACTIVE'))
        db.conn.commit()
        db.conn.close()
        db.conn = None
        return GeneratedIds(user_ids=driver_ids, addr_ids=addr_ids)

    # @staticmethod
    # def delete_drivers(db: Database, ids: GeneratedIds):
    #     db.open_connection()
    #     db.conn.jconn.setAutoCommit(False)
    #     with db.conn.cursor() as cursor:
    #         for driver_id in ids.user_ids:
    #             cursor.execute('DELETE FROM driver WHERE id = UNHEX(?)', (driver_id,))
    #     db.conn.commit()
    #     db.conn.close()
    #     db.conn = None
    #
    #     UserData.delete_users(db, ids)


class DeliveryData:
    @staticmethod
    def create_deliveries(db: Database, count: int) -> GeneratedIds:
        driver_ids = DriverData.create_drivers(db, count).user_ids
        address_ids = AddressData.create_addresses(db, count).addr_ids
        delivery_ids = []
        curr_id = get_last_insert_id(db, 'delivery')

        db.open_connection()
        with db.conn.cursor() as cursor:
            for _ in range(count):
                driver_id = random.choice(driver_ids)
                address_id = random.choice(address_ids)
                curr_id += 1
                cursor.execute("INSERT INTO delivery (id,address_id,driver_id) "
                               "VALUES (?, ?, UNHEX(?))",
                               (curr_id, address_id, driver_id))
                delivery_ids.append(curr_id)
        db.conn.close()
        db.conn = None
        return GeneratedIds(deliv_ids=delivery_ids, user_ids=driver_ids, addr_ids=address_ids)

    # @staticmethod
    # def delete_deliveries(db: Database, ids: GeneratedIds):
    #     db.open_connection()
    #     db.conn.jconn.setAutoCommit(False)
    #     with db.conn.cursor() as cursor:
    #         for delivery_id in ids.deliv_ids:
    #             cursor.execute('DELETE FROM delivery WHERE id = ?', (delivery_id,))
    #     db.conn.commit()
    #     db.conn.close()
    #     db.conn = None
    #
    #     DriverData.delete_drivers(db, ids)
    #     AddressData.delete_addresses(db, ids)