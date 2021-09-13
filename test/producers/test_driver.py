import uuid

import pymysql

from app.db.config import Config
from app.db.database import Database
from app.producers.driver import Driver, DriverProducer

database = Database(Config())
database.open_connection()
producer = DriverProducer(database, "../../app/data/first_names.txt", "../../app/data/last_names.txt")


def test_driver_properties():
    driverId = uuid.uuid4().bytes
    userId = uuid.uuid4().bytes
    locationId = uuid.uuid4().bytes
    firstName = "Kyle"
    lastName = "Power"
    phone = "555-506-2967"
    dob = "10/15/96"
    licenseNum = "494586"
    rating = 2.456

    driver = Driver(producer, driverId, userId, locationId, firstName, lastName, phone, dob, licenseNum, rating)
    assert driver.driverId == driverId
    assert driver.userId == userId
    assert driver.locationId == locationId
    assert driver.firstName == firstName
    assert driver.lastName == lastName
    assert driver.phone == phone
    assert driver.dob == dob
    assert driver.licenseNum == licenseNum
    assert driver.rating == rating


def test_get_items_from_file():
    data = producer.get_items_from_file("../../app/data/first_names.txt")
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
                cursor.execute("SELECT driverId FROM scrumptious.driver")
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
    producer.create_drivers(create_quantity)
    end_quantity = len(get_driver_ids())

    assert start_quantity + create_quantity == end_quantity


def test_create_random():
    driver = Driver(producer)
    driver.create_random()
    assert isinstance(driver.driverId, bytes)
    assert isinstance(driver.userId, bytes)
    assert isinstance(driver.locationId, bytes)
    assert isinstance(driver.firstName, str)
    assert isinstance(driver.lastName, str)
    assert isinstance(driver.phone, str)
    assert isinstance(driver.dob, str)
    assert isinstance(driver.licenseNum, str)
    assert isinstance(driver.rating, float)


def test_create_dob():
    driver = Driver(producer)
    assert isinstance(driver.create_dob(), str)


def test_create_phone():
    driver = Driver(producer)
    assert isinstance(driver.create_phone(), str)
