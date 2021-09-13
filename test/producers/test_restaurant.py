import pymysql

from app.db.config import Config
from app.db.database import Database
from app.producers.restaurant import RestaurantProducer

database = Database(Config())
database.open_connection()
producer = RestaurantProducer(database, "../../app/data/addresses.csv", "../../app/data/restaurant-names.txt")


def test_get_addresses_from_csv():
    addrs = producer.get_addresses_from_csv()
    assert isinstance(addrs, list)


def test_get_restaurant_names_from_file():
    names = producer.get_addresses_from_csv()
    assert isinstance(names, list)


def test_get_all_from():
    users = producer.get_all_from("user")
    assert isinstance(users, list)


def test_create_random_address():
    def get_addr_ids():
        try:
            with database.conn.cursor() as cursor:
                records = []
                cursor.execute("SELECT addressId FROM address")
                result = cursor.fetchall()
                for row in result:
                    records.append(row)
                cursor.close()
                return records

        except pymysql.MySQLError as e:
            print('Error trying to test database')
            print(e)
            assert False

    start_quantity = len(get_addr_ids())
    producer.create_random_address()
    end_quantity = len(get_addr_ids())
    assert end_quantity > start_quantity


def test_create_restaurants():
    def get_restaurant_ids():
        try:
            with database.conn.cursor() as cursor:
                records = []
                cursor.execute("SELECT restaurantId FROM restaurant")
                result = cursor.fetchall()
                for row in result:
                    records.append(row)
                cursor.close()
                return records

        except pymysql.MySQLError as e:
            print('Error trying to test database')
            print(e)
            assert False

    create_quantity = 10
    start_quantity = len(get_restaurant_ids())
    producer.create_restaurants(create_quantity)
    end_quantity = len(get_restaurant_ids())
    assert end_quantity - start_quantity == create_quantity
