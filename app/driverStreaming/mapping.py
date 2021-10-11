import json

import googlemaps
from jaydebeapi import Error

from app.db.config import Config
from app.db.database import Database
from app.stream import StreamBuilder


def parse_directions(directions):
    leg = directions[0]["legs"][0]
    steps = []
    for step in leg["steps"]:
        steps.append({
            "distance": step["distance"]["value"],
            "duration": step["duration"]["value"],
            "end_location": step["end_location"],
            "start_location": step["start_location"],
            "instructions": step["html_instructions"],
            "maneuver": step["maneuver"] if "maneuver" in step else "None",
        })

    return steps


def get_api_key():
    with open("./maps-api-key.txt") as file:
        return file.readline()


class DriverDirectionHandler:
    def __init__(self, api_key):
        self.stream_builder = StreamBuilder("driver-direction-output")
        self.kinesis = self.stream_builder.get_stream()

        self.gmaps = googlemaps.Client(key=api_key)

        self.database = Database(Config())
        self.database.open_connection()

        self.sent_packets = []

    def handle_message(self, data):
        if data["type"] == "directions":
            self.handle_directions_message(data)

    def get_address(self, address_id):
        try:
            with self.database.conn.cursor() as cursor:
                sql = "SELECT * from address WHERE id=?;"
                cursor.execute(sql, [address_id])
                value = cursor.fetchall()[0]
                cursor.close()
                return value
        except Error as e:
            print(e)

    def handle_directions_message(self, data):
        [address_id, line1, line2, city, state, zip] = self.get_address(data["destinationId"])
        address_name = line1 + " " + (line2 if line2 is not None else "") + ", " + city + " " + state + ". " + zip
        directions = self.gmaps.directions(data["location"], address_name)
        parsed = parse_directions(directions)

        reply = {
            "driverId": data["driverId"],
            "type": "directions",
            "directions": parsed
        }

        if len(parsed) == 1:
            reply["type"] = "arrived"

        self.emit(reply)

    def emit(self, message):
        self.kinesis.put_record(StreamName=self.stream_builder.stream_name, Data=json.dumps(message),
                                PartitionKey=self.stream_builder.stream_name)
        print(message)
