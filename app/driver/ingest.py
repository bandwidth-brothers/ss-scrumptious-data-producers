import argparse

from app.driver.model import Driver
from app.ingestBase import Ingest


class DriverIngestArgParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                              description="""Ingests driver data from a CSV, XML, or JSON file.
The required fields are address_id,first_name,last_name,phone,dob,license_num,rating,status""")
        self.parser.add_argument("--path", type=str, help="Filepath to the csv, json, or xml to import")

    def get_args(self):
        return self.parser.parse_args()


def handle_data(ingest: Ingest, data: dict):
    return [
        data["user_id"], data["address_id"], data["first_name"], data["last_name"], data["phone"],
        data["dob"], data["license_num"], data["rating"], data["status"],
    ]


def main():
    args = ["user_id", "address_id", "first_name", "last_name", "phone", "dob", "license_num", "rating", "status"]
    user_args = vars(DriverIngestArgParser().get_args())
    path = user_args["path"] or "./app/data/driver-ingest-test.csv"

    ingest = Ingest(path, args, "drivers", Driver, handle_data)
    ingest.parse()


if __name__ == '__main__':
    main()
