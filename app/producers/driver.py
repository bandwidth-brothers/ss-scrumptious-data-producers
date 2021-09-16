import argparse
import logging as log
import random
from datetime import date

import pymysql

from app.db.config import Config
from app.db.database import Database


class DriverArgParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                              description="""Randomly create a given number of drivers in the 
MySQL database. Each driver will pull from the employees in the user table, and addresses from the addresses table
First and last names are pulled from a file, which can be specified using command line arguments 
""")
        self.parser.add_argument('--first-names', type=str,
                                 help="Filepath to a txt document with a list of first names to draw from")
        self.parser.add_argument("--last-names", type=str,
                                 help="Filepath to a txt document with a list of last names to draw from")
        self.parser.add_argument("--num", type=int, help="Number of drivers to create")

    def get_args(self):
        return self.parser.parse_args()


class DriverProducer:
    def __init__(self, database: Database, first_name_path=None, last_name_path=None):
        self.first_name_path = first_name_path or "./app/data/first_names.txt"
        self.last_name_path = last_name_path or "./app/data/last_names.txt"
        self.database = database

        self.user_ids = self.get_driver_users()
        self.address_ids = self.get_address_ids()

        self.first_names = self.get_items_from_file(self.first_name_path)
        self.last_names = self.get_items_from_file(self.last_name_path)

        if len(self.user_ids) == 0:
            log.error("No driver users are present in the database!")
            return

        if len(self.address_ids) == 0:
            log.error("No addresses found in the database!")
            return

    def get_items_from_file(self, path: str):
        with open(path) as file:
            return file.readlines()

    def get_address_ids(self):
        try:
            with self.database.conn.cursor() as cursor:
                records = []
                cursor.execute("SELECT addressId FROM address")
                result = cursor.fetchall()
                for row in result:
                    records.append(row[0])
                cursor.close()
                return records
        except pymysql.MySQLError as e:
            log.error("A database error occurred when trying to fetch users")
            print(e)

    def get_driver_users(self):
        try:
            with self.database.conn.cursor() as cursor:
                records = []
                cursor.execute(
                    "SELECT user.userId FROM user LEFT JOIN driver on user.userId=driver.driverId WHERE driver.driverId IS NULL;")
                result = cursor.fetchall()
                for row in result:
                    records.append(row[0])
                cursor.close()
                return records
        except pymysql.MySQLError as e:
            log.error("A database error occurred when trying to fetch users")
            print(e)

    def create_drivers(self, quantity: int):
        if quantity is None or quantity < 0:
            driver = Driver(self)
            driver.create_random()
            print(driver)
            print("Example output, use the --num option to specify how many should be created")
        else:
            for i in range(quantity):
                driver = Driver(self)
                driver.create_random()
                driver.save()
            print(f"Created {quantity} drivers in the database!")


class Driver:
    def __init__(self,
                 producer: DriverProducer,
                 driverId: bytes = None,
                 locationId: bytes = None,
                 firstName: str = None,
                 lastName: str = None,
                 phone: str = None,
                 dob: str = None,
                 licenseNum: str = None,
                 rating: float = None
                 ):
        self.producer = producer
        self.driverId = driverId
        self.locationId = locationId
        self.firstName = firstName
        self.lastName = lastName
        self.email = f"{firstName}.{lastName}@mail.com" if firstName is not None and lastName is not None else None
        self.phone = phone
        self.dob = dob
        self.licenseNum = licenseNum
        self.rating = rating

    def create_random(self):
        self.driverId = random.choice(self.producer.user_ids)
        self.locationId = random.choice(self.producer.address_ids)
        self.firstName = random.choice(self.producer.first_names)
        self.lastName = random.choice(self.producer.last_names)
        self.email = self.firstName + "." + self.lastName + "@mail.com"
        self.phone = self.create_phone()
        self.dob = self.create_dob()
        self.licenseNum = str(random.randint(10000, 99999))
        self.rating = random.random() * 5

    def save(self):
        try:
            with self.producer.database.conn.cursor() as cursor:
                sql = "INSERT INTO driver (driverId, addressId, firstName, lastName, " \
                      "phone, dob, licenseNum, rating, picture, status) " \
                      "VALUES (?,?,?,?,?,?,?,?,?,?)"
                values = (
                    self.driverId, self.locationId, self.firstName, self.lastName,
                    self.phone, self.dob, self.licenseNum, self.rating, "https://temp.url/", "active"
                )

                cursor.execute(sql, values)
                cursor.close()
        except pymysql.MySQLError as e:
            log.error("Error creating a driver")
            log.error(e)

    def create_dob(self):
        return date.today().strftime("%d/%m/%Y")

    def create_phone(self):
        phone = "xxx-xxx-xxxx"
        output = [x if x != "x" else str(random.randint(1, 9)) for x in phone]
        return "".join(output)

    def __str__(self):
        return f"User ID: {self.userId}, Location ID: {self.locationId}, " \
               f"Name: {self.firstName} {self.lastName}, Phone: {self.phone}, " \
               f"DOB: {self.dob}, License Plate: {self.licenseNum}, Rating: {self.rating}"


def main():
    db = Database(Config())
    db.open_connection()

    args = vars(DriverArgParser().get_args())
    producer = DriverProducer(db, args["first_names"], args["last_names"])
    producer.create_drivers(args["num"])


if __name__ == '__main__':
    main()
