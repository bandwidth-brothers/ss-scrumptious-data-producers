import csv
import json
import xml.etree.ElementTree as ET
from typing import List

from jaydebeapi import Error
from pyspark import RDD
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext

from app.db.config import Config
from app.db.database import Database
from app.producers.helpers import print_items_and_confirm
from app.restaurant.model import Restaurant
from app.stream import StreamBuilder, set_spark_env

VALID_TYPES = ["csv", "json", "xml"]


def handle_rdd(item, rdd: RDD):
    rdd.foreach(lambda x: handle_stream_data(item, x))


def handle_stream_data(item, data):
    database = Database(Config())
    database.open_connection()

    new_item = item()
    new_item.from_stream_data(data)
    valid = new_item.save(database)
    print(("Created: " if valid else "Error creating: ") + new_item.__str__())


class Ingest:
    """
    filepath - Path to the file to parse, must have an extension that matches one of VALID_TYPES
    target_args - List of names to look for in a file, will be passed as a dict to handle_data
    item - One of the data models with a save method
    handle_data - A method to call for each item, should return a list to be used to construct item
    """

    def __init__(self, ):
        self.type: str = ""
        self.path: str = ""
        self.target_args: List[str] = []
        self.item = None
        self.handle_data = None
        self.item_type: str = ""

        self.database = Database(Config())
        self.database.open_connection()

    def init_file_parse(self, filepath: str, target_args: List[str], item_type: str, item, handle_data):
        self.type = filepath[filepath.rfind(".") + 1:]
        self.path = filepath
        self.target_args = target_args
        self.item = item
        self.handle_data = handle_data
        self.item_type = item_type

        if self.type not in VALID_TYPES:
            valid = ", ".join(VALID_TYPES)
            print(f"\"{self.type}\" is not a valid file type. Please use one of the following: {valid}")
            exit()

    def init_stream(self, item):
        self.item = item

    def from_stream(self, obj_type: str):
        set_spark_env()
        print("Starting spark stream")
        spark = SparkSession \
            .builder \
            .appName("ingestStreaming") \
            .getOrCreate()

        ssc = StreamingContext(spark.sparkContext, 1)

        stream = StreamBuilder("data-producers").get_spark_stream(ssc)
        stream \
            .map(lambda x: json.loads(x)) \
            .filter(lambda x: x["type"] == obj_type) \
            .foreachRDD(lambda data: handle_rdd(self.item, data))
        ssc.start()
        ssc.awaitTermination()

    def parse(self):
        data = []
        if self.type == "csv":
            data = self.handle_csv()
        elif self.type == "json":
            data = self.handle_json()
        elif self.type == "xml":
            data = self.handle_xml()

        self.create_and_save(data)

    def create_and_save(self, data: List[List[any]]):
        items = []
        for entry in data:
            items.append(self.item(*entry))

        answer = print_items_and_confirm(items=items, item_type=self.item_type)
        num_created = 0
        if answer.strip().lower() == "y":
            for item in items:
                if item.save(self.database):
                    num_created += 1
            print(f"Created {num_created} {self.item_type} in the database")

    def try_resolve_csv_headers(self, row: List[str]):
        default_mapping = []
        for i in range(len(self.target_args)):
            default_mapping.append(self.target_args[i])

        mapping = []
        for i in range(len(row)):
            if row[i] in default_mapping:
                mapping.append(row[i])

        use_default = False
        for key in default_mapping:
            if key not in mapping:
                default_format = ", ".join(self.target_args)
                print("CSV is either header-less, or is missing some required fields");
                print(f"Using default format: {default_format}")
                use_default = True
                break

        if use_default:
            return [True, default_mapping]
        else:
            return [False, mapping]

    def parse_row(self, row, row_number, mapping):
        data_dict = {}
        if len(row) < len(mapping):
            print(f"CSV data length miss-match, got {len(row)}, needed {len(mapping)} for row {row_number}")
            return
        for j in range(len(mapping)):
            data_dict[mapping[j]] = row[j]

        # Make sure that all values are present
        is_valid = True
        for arg in self.target_args:
            if arg not in data_dict.keys():
                print(f"{arg} is missing in CSV row {row_number}")
                is_valid = False
                break

        if is_valid:
            parsed = self.handle_data(self, data_dict)
            return parsed

    def handle_json(self):
        parsed_data = []

        with open(self.path) as json_file:
            data = json.load(json_file)
            for entry in data:
                is_valid = True

                for arg in self.target_args:
                    if arg not in entry:
                        is_valid = False
                        print(f"Entry is missing key {arg}")

                if is_valid:
                    parsed_data.append(self.handle_data(self, entry))

        return parsed_data

    def handle_csv(self):
        rows = []
        with open(self.path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                rows.append(row)

        header = rows[0]
        if header is None:
            print("Target file appears to have no data")
            exit()
        [is_default, mapping] = self.try_resolve_csv_headers(header)
        data = []
        for i in range(len(rows)):
            if not is_default and i == 0:
                continue
            parsed = self.parse_row(rows[i], i, mapping)
            if parsed is not None:
                data.append(parsed)

        return data

    def handle_xml(self):
        tree = ET.parse(self.path)
        data = tree.getroot()
        item_data = []
        for entry in data:
            data_dict = {}
            for key in entry:
                data_dict[key.tag] = key.text

            is_valid = True
            for arg in self.target_args:
                if arg not in data_dict:
                    print(f"{arg} is missing!")
                    is_valid = False

            if is_valid:
                item_data.append(self.handle_data(self, data_dict))

        return item_data


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


def main():
    args = ["street", "city", "state", "zip", "owner_id", "name", "rating", "price_category",
            "phone", "is_active", "picture"]
    ingest = Ingest()
    ingest.init_stream(Restaurant)
    ingest.from_stream("restaurant")
    # ingest.init_file_parse("./app/data/restaurants-ingest-test.xml", args, "restaurants", Restaurant, handle_data)
    # ingest.parse()


if __name__ == '__main__':
    main()
