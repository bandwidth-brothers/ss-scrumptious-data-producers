import json

import googlemaps
import requests as requests
from geopy import distance
from jaydebeapi import Error

from app.db.config import Config
from app.db.database import Database
from app.stream import StreamBuilder

APPROACH_DIST = 5  # Distance to alert aproach from in km
APPROACH_NOTIF_URL = "http://localhost:8080/driver_aproaching/"


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

    return [steps, leg["duration"]["value"], leg["distance"]["value"], leg["end_location"]]


def gps_to_tuple(point):
    return point["lat"], point["lng"]


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
        if data["type"] == "directions" or data["type"] == "start":
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

    def get_destination_id_from_order(self, order_id, target):
        try:
            with self.database.conn.cursor() as cursor:
                sql = ""
                if target == "restaurant":
                    sql = "SELECT r.address_id from scrumptious.order o JOIN scrumptious.restaurant r on r.id=o.restaurant_id where o.id=UNHEX(?);"
                else:
                    sql = "SELECT d.address_id from scrumptious.order o JOIN scrumptious.delivery d on d.id=o.delivery_id where o.id=UNHEX(?)"
                cursor.execute(sql, [order_id])
                value = cursor.fetchall()[0][0]
                cursor.close()
                return value
        except Error as e:
            print(e)

    def check_for_approach(self, current, dest, data):
        dist = distance.distance(gps_to_tuple(current), gps_to_tuple(dest)).km
        if dist < APPROACH_DIST:
            packet = {
                "driverId": data["driverId"],
                "orderId": data["orderId"],
                "type": "approach",
                "target": data["target"],
                "distance": dist
            }
            self.send_approach_req(packet, data)
            self.emit(packet)

    def handle_directions_message(self, data):
        destination_id = self.get_destination_id_from_order(data["orderId"], data["target"])
        [address_id, line1, line2, city, state, zip] = self.get_address(destination_id)
        address_name = line1 + " " + (line2 if line2 is not None else "") + ", " + city + " " + state + ". " + zip
        directions = self.gmaps.directions(data["location"], address_name)
        [parsed, duration, drive_dist, end_loc] = parse_directions(directions)

        self.check_for_approach(data["location"], end_loc, data)

        reply = {
            "driverId": data["driverId"],
            "orderId": data["orderId"],
            "type": "directions" if data["type"] == "directions" else "start",
            "directions": parsed,
            "distance": drive_dist,
            "duration": duration
        }

        if len(parsed) == 1:
            if reply["type"] == "start":
                self.emit(reply)
            reply["type"] = "arrived"

        self.emit(reply)

    def send_approach_req(self, packet, data):
        id = "driverId"
        body = {
            "target": data["target"],
            "currentLoc": data["location"],
            "type": "approach",
            "distance": packet["distance"]
        }
        req = requests.post(
            url=APPROACH_NOTIF_URL + packet[id],
            data=json.dumps(body)
        )
        if req.status_code != 200:
            print(f"Approach request for {packet[id]} failed due to {req.status_code}")

    def emit(self, message):
        self.kinesis.put_record(StreamName=self.stream_builder.stream_name, Data=json.dumps(message),
                                PartitionKey=self.stream_builder.stream_name)
        print(message)


def run():
    directions = DriverDirectionHandler(get_api_key())
    directions.handle_message({
        "driverId": "D3A6E60BFECF4C4393F9EEFBC6E8D48C",
        "type": "start",
        "target": "customer",
        "orderId": "3100000000000000",
        "location": {
            "lat": 38.7767523,
            "lng": -77.12479549999999
        }
    })


if __name__ == "__main__":
    run()
