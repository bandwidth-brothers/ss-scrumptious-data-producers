import uuid

import pymysql

from app.db.config import Config
from app.db.database import Database
from app.driver.producer import Driver, DriverProducer
from app.producers.users import UsersProducer, UserGenerator, User

user_database_conn = Database(Config())
user_database_conn.open_connection()

# Setup users needed to run tests
user_producer = UsersProducer(user_database_conn)
for i in range(10):
    user = UserGenerator.generate_user(role=User.Role.DRIVER)
    user_producer.save_user(user)

database = Database(Config())
database.open_connection()
producer = DriverProducer(database, "./app/data/first_names.txt", "./app/data/last_names.txt")


def test_driver_properties():
    id = uuid.uuid4().bytes
    address_id = uuid.uuid4().bytes
    first_name = "Kyle"
    last_name = "Power"
    phone = "555-506-2967"
    dob = "10/15/96"
    license_num = "494586"
    rating = 2.456

    driver = Driver(id, address_id, first_name, last_name, phone, dob, license_num, rating)
    assert driver.id == id
    assert driver.address_id == address_id
    assert driver.first_name == first_name
    assert driver.last_name == last_name
    assert driver.phone == phone
    assert driver.dob == dob
    assert driver.license_num == license_num
    assert driver.rating == rating


def test_get_items_from_file():
    data = producer.get_items_from_file("./app/data/first_names.txt")
    assert isinstance(data, list)


def test_get_address_ids():
    ids = producer.get_address_ids()
    assert isinstance(ids, list)


def test_get_driver_users():
    ids = producer.get_address_ids()
    assert isinstance(ids, list)


def test_create_drivers():
    def get_driver_ids():
        try:
            with database.conn.cursor() as cursor:
                records = []
                cursor.execute("SELECT id FROM scrumptious.driver")
                result = cursor.fetchall()
                for row in result:
                    records.append(row)
                cursor.close()
                return records

        except pymysql.MySQLError as e:
            print('Error trying to test database')
            print(e)

    create_quantity = 10
    start_quantity = len(get_driver_ids())
    for _ in range(create_quantity):
        driver = Driver()
        driver.create_random(producer)
        driver.save(database)

    end_quantity = len(get_driver_ids())

    assert start_quantity + create_quantity == end_quantity


def test_create_random():
    driver = Driver()
    driver.create_random(producer)
    assert isinstance(driver.address_id, int)
    assert isinstance(driver.first_name, str)
    assert isinstance(driver.last_name, str)
    assert isinstance(driver.phone, str)
    assert isinstance(driver.dob, str)
    assert isinstance(driver.license_num, str)
    assert isinstance(driver.rating, float)


def test_create_dob():
    driver = Driver()
    assert isinstance(driver.create_dob(), str)


def test_create_phone():
    driver = Driver()
    assert isinstance(driver.create_phone(), str)
