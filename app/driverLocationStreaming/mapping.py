import json

import googlemaps
from jaydebeapi import Error

from app.db.config import Config
from app.db.database import Database


def get_api_key():
    with open("./maps-api-key.txt") as file:
        return file.readline()


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


class DriverDirectionHandler:
    def __init__(self, api_key: str, testing_data_path: str):
        self.gmaps = googlemaps.Client(key=api_key)

        self.database = Database(Config())
        self.database.open_connection()

        self.sent_packets = []

        with open(testing_data_path) as json_file:
            data = json.load(json_file)
            for message in data:
                self.handle_message(message)

        with open('./app/data/driverStreamOut.json', 'w') as f:
            json.dump(self.sent_packets, f)

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
        print(message)
        self.sent_packets.append(message)


def main():
    api_key = get_api_key()
    direction_handler = DriverDirectionHandler(api_key, "./app/data/driverUpdates.json")


if __name__ == "__main__":
    main()
