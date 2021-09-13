import argparse
import csv
import logging as log
import random
import string
import uuid

import pymysql

from app.db.config import Config
from app.db.database import Database


class RestaurantArgParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                              description="""Randomly create a given number of restaurants in the 
MySQL database. Each restaurant will automatically generate their address from a (CSV) file, you may provide the --addrs 
option to point to the file you wish to use for this. Restaurant names are randomly chosen from a text document. 
If you wish to use a different file than the default, use the --names argument 
""")
        self.parser.add_argument('--addrs', type=str, help="""Filepath to a CSV with addresses to pull from
File should not have a header, and have the following columns (address,city,state,zip)""")
        self.parser.add_argument("--names", type=str,
                                 help="Filepath to a txt document with a list of names to draw from")
        self.parser.add_argument("--num", type=int, help="Number of restaurants to create")

    def get_args(self):
        return self.parser.parse_args()


class RestaurantProducer:
    def __init__(self, database: Database, addr_csv_path=None, rest_names_path=None):
        self.addr_csv_path = addr_csv_path or "../data/addresses.csv"
        self.rest_names_path = rest_names_path or "../data/restaurant-names.txt"
        self.database = database

        # [address,city,state,zip]
        self.addresses = self.get_addresses_from_csv()

        self.names = self.get_restaurant_names_from_file()

        self.restaurant_owners = self.get_all_from("restaurant_owner")

        if len(self.restaurant_owners) == 0:
            log.error("No restaurant owners are present in the database!")
            return

    def get_addresses_from_csv(self) -> list:
        addresses = []
        with open(self.addr_csv_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                addresses.append(row)
        return addresses

    def get_restaurant_names_from_file(self) -> list:
        with open(self.rest_names_path) as file:
            return file.readlines()

    def get_all_from(self, table) -> list:
        try:
            with self.database.conn.cursor() as cursor:
                records = []
                cursor.execute("SELECT * FROM " + table)
                result = cursor.fetchall()
                for row in result:
                    records.append(row)
                cursor.close()
                return records
        except pymysql.MySQLError as e:
            print(e)

    def create_random_address(self):
        uid = uuid.uuid4().bytes
        try:
            addr = random.choice(self.addresses)
            with self.database.conn.cursor() as cursor:
                sql = "INSERT INTO address (addressId,line1,line2,city,state,zip) " \
                      "VALUES (%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, (uid, addr[0], "", addr[1], addr[2], addr[3]))
                self.database.conn.commit()
                cursor.close()
        except pymysql.MySQLError as e:
            print(e)
        finally:
            return uid

    def create_restaurants(self, quantity: int):
        if quantity is None or quantity < 0:
            restaurant = Restaurant(self)
            restaurant.create_random()
            print(restaurant)
            print("Example output, use the --num option to specify how many should be created")
        else:
            for i in range(quantity):
                restaurant = Restaurant(self)
                restaurant.create_random()
                restaurant.save()
            print(f"Created {quantity} restaurants in the database!")


class Restaurant:

    def __init__(self,
                 producer: RestaurantProducer,
                 restaurantId: bytes = None,
                 addressId: bytes = None,
                 restaurantOwnerId: bytes = None,
                 name: string = None,
                 rating: float = None,
                 priceCategory: int = None,
                 phone: string = None,
                 isActive: bool = None,
                 restaurantLogo: string = None
                 ):
        self.producer = producer
        self.restaurantId = restaurantId
        self.addressId = addressId
        self.restaurantOwnerId = restaurantOwnerId
        self.name = name
        self.rating = rating
        self.priceCategory = priceCategory
        self.phone = phone
        self.isActive = isActive
        self.restaurantLogo = restaurantLogo

    def create_random(self):
        self.restaurantId = uuid.uuid4().bytes
        self.addressId = self.producer.create_random_address()
        self.restaurantOwnerId = random.choice(self.producer.restaurant_owners)[0]
        self.name = random.choice(self.producer.names)
        self.rating = random.random() * 5
        self.priceCategory = random.choice((1, 2, 3))
        self.phone = self.create_phone()
        self.isActive = random.choice((True, False))

    def create_phone(self):
        phone = "xxx-xxx-xxxx"
        output = [x if x != "x" else str(random.randint(1, 9)) for x in phone]
        return "".join(output)

    def save(self):
        try:
            with self.producer.database.conn.cursor() as cursor:
                sql = "INSERT INTO restaurant (restaurantId, addressId, restaurantOwnerId, name, rating, priceCategory, phone, isActive, restaurantLogo) " \
                      "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                values = (
                    self.restaurantId, self.addressId, self.restaurantOwnerId, self.name, self.rating,
                    self.priceCategory,
                    self.phone, self.isActive, self.restaurantLogo)

                cursor.execute(sql, values)
                self.producer.database.conn.commit()
                cursor.close()
        except pymysql.MySQLError as e:
            print(e)

    def __str__(self):
        return f"ID: {self.restaurantId}\nAddress ID: {self.addressId}\n" \
               f"Owner ID: {self.restaurantOwnerId}\nName: {self.name}\n" \
               f"Rating: {self.rating}\nPrice category: {self.priceCategory}\n" \
               f"Phone: {self.phone}\nIs Active: {self.isActive}\nLogo: {self.restaurantLogo}"


def main():
    db = Database(Config())
    db.open_connection()

    args = vars(RestaurantArgParser().get_args())
    producer = RestaurantProducer(db, args["addrs"], args["names"])
    producer.create_restaurants(args["num"])


if __name__ == '__main__':
    main()
