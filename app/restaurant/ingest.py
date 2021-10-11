import argparse

from jaydebeapi import Error

from app.ingestBase import Ingest
from app.restaurant.model import Restaurant
from app.restaurant.otherDataModel import OtherRestaurantData


class RestaurantIngestArgParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                              description="""Ingests restaurant data from a CSV, XML, or JSON file
The required fields are street, city, state, zip, owner_id, name, rating, 
price_category, phone, is_active, picture.
Additionally restaurant reviews can be ingested using the --reviews flag, which must be a XML or JSON file 
with the properties restaurant_id, reviews
""")
        self.parser.add_argument("--path", type=str,
                                 help="Filepath to the csv, json, or xml to import. If path is left blank then it "
                                      "will pull data from the spark stream instead")
        self.parser.add_argument("--reviews", type=str, help="Filepath to the json, or xml to import for reviews")

    def get_args(self):
        return self.parser.parse_args()


def create_address(database, street, city, state, zip):
    uid = 0
    try:
        with database.conn.cursor() as cursor:
            sql = "INSERT INTO address (line1,line2,city,state,zip) " \
                  "VALUES (?,?,?,?,?);"
            cursor.execute(sql, (street, "", city, state, zip))
            cursor.execute("SELECT LAST_INSERT_ID();")
            uid = cursor.fetchall()[0][0]
            cursor.close()
    except Error as e:
        print(e)
    finally:
        return uid


def handle_data(ingest: Ingest, data: dict):
    address_id = create_address(ingest.database, data["street"], data["city"], data["state"], data["zip"])
    return [
        None, address_id, data["owner_id"], data["name"], float(data["rating"]),
        int(data["price_category"]), data["phone"], int(data["is_active"]), data["picture"]
    ]


def handle_review_data(ingest: Ingest, data: dict):
    print(data)
    pass


def main():
    args = ["street", "city", "state", "zip", "owner_id", "name", "rating", "price_category",
            "phone", "is_active", "picture"]

    review_args = ["restaurant_id", "reviews"]

    user_args = vars(RestaurantIngestArgParser().get_args())

    if "path" in user_args and user_args["path"] is not None:
        path = user_args["path"]
        ingest = Ingest()
        ingest.init_file_parse(path, args, "restaurants", Restaurant, handle_data)
        ingest.parse()

    elif "reviews" in user_args and user_args["reviews"] is not None:
        path = user_args["reviews"]
        ingest = Ingest()
        ingest.init_file_parse(path, review_args, "restaurant reviews", OtherRestaurantData, handle_review_data)
        ingest.parse()

    else:
        ingest = Ingest()
        ingest.init_stream(Restaurant)
        ingest.from_stream("restaurant")


if __name__ == '__main__':
    main()
