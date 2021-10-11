import argparse
import logging as log
from time import sleep

from jaydebeapi import Error

from app.db.config import Config
from app.db.database import Database
from app.driver.model import Driver
from app.producers.helpers import print_items_and_confirm


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
        self.parser.add_argument("--target", type=str, choices=["database", "stream"], default="database",
                                 help="If the data should be stored directly in the database, or instead streamed")

    def get_args(self):
        return self.parser.parse_args()


class DriverProducer:
    def __init__(self, database: Database, first_name_path=None, last_name_path=None, target="database"):
        self.target = target
        self.first_name_path = first_name_path or "./app/data/first_names.txt"
        self.last_name_path = last_name_path or "./app/data/last_names.txt"
        self.database = database

        self.user_ids = self.get_driver_users()
        self.address_ids = self.get_address_ids()

        self.first_names = self.get_items_from_file(self.first_name_path)
        self.last_names = self.get_items_from_file(self.last_name_path)

        if len(self.user_ids) == 0:
            log.error("No users are present in the database that can be assigned as drivers!")
            exit()

        if len(self.address_ids) == 0:
            log.error("No addresses found in the database!")
            exit()

    def get_items_from_file(self, path: str):
        with open(path) as file:
            lines = file.readlines()
            clean_lines = []
            # Remove ending newline if it exists
            for line in lines:
                if line[len(line) - 1] == "\n":
                    line = line[:len(line) - 1]
                clean_lines.append(line)
            return clean_lines

    def get_address_ids(self):
        try:
            with self.database.conn.cursor() as cursor:
                records = []
                cursor.execute("SELECT id FROM address")
                result = cursor.fetchall()
                for row in result:
                    records.append(row[0])
                cursor.close()
                return records
        except Error as e:
            log.error("A database error occurred when trying to fetch users")
            print(e)

    def get_driver_users(self):
        try:
            with self.database.conn.cursor() as cursor:
                records = []
                cursor.execute(
                    "SELECT HEX(user.id) FROM user LEFT JOIN driver on user.id=driver.id WHERE driver.id IS NULL;")
                result = cursor.fetchall()
                for row in result:
                    records.append(row[0])
                cursor.close()
                return records
        except Error as e:
            log.error("A database error occurred when trying to fetch users")
            print(e)

    def create_in_stream(self, quantity: int):
        if quantity is None:
            print("Creating one driver per second")
            while True:
                driver = Driver()
                driver.producer = self
                driver.create_random(self)
                driver.stream()
                print(driver)
                sleep(1)
        else:
            created = []
            for i in range(quantity):
                driver = Driver()
                driver.producer = self
                driver.create_random(self)
                created.append(driver)

            answer = print_items_and_confirm(items=created, item_type="drivers")
            if answer.strip().lower() == "y":
                for driver in created:
                    driver.stream()

                print(f"Sent {len(created)} drivers to the data stream!")
            else:
                print(f"No items created")

    def create_drivers(self, quantity: int):
        if self.target == "stream":
            self.create_in_stream(quantity)
            return

        if quantity is None or quantity < 0:
            driver = Driver()
            driver.create_random(self)
            print(driver)
            print("Example output, use the --num option to specify how many should be created")
        else:
            created = []
            for i in range(quantity):
                driver = Driver()
                driver.create_random(self)
                created.append(driver)

            answer = print_items_and_confirm(items=created, item_type="drivers")
            num_created = 0
            if answer.strip().lower() == "y":
                for driver in created:
                    if driver.save(self.database):
                        num_created += 1

                print(f"Created {num_created} drivers in the database!")
            else:
                print(f"No items created")


def main():
    db = Database(Config())
    db.open_connection()

    args = vars(DriverArgParser().get_args())
    producer = DriverProducer(db, args["first_names"], args["last_names"], args["target"])
    producer.create_drivers(args["num"])


if __name__ == '__main__':
    main()
