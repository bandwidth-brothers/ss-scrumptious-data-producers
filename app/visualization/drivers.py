import argparse
import os
from datetime import datetime

import boto3
import matplotlib.pyplot as plt
from dotenv import load_dotenv


class VisualizationArgParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                              description="""Displays a graph showing some driver metrics, can be 
constrained to a specific driver, and specific time frames""")
        self.parser.add_argument("--miles-per-day", action="store_true",
                                 help="Displays how many miles miles were driven by drivers in the time frame")
        self.parser.add_argument("--time-inaccuracy", action="store_true",
                                 help="Displays the difference between predicted and "
                                      "actual time for deliveries in the time frame")
        self.parser.add_argument("--mph", action="store_true",
                                 help="Displays the estimated, and actual delivery speeds")

        self.parser.add_argument("--driverId", type=str, help="Limits the shown values to a single driver")

        self.parser.add_argument("--before", type=lambda s: datetime.strptime(s, '%m/%d/%Y'),
                                 help="Upper bound of dates to show (m/d/y)")
        self.parser.add_argument("--after", type=lambda s: datetime.strptime(s, '%m/%d/%Y'),
                                 help="Lower bound of dates to show (m/d/y)")

    def get_args(self):
        return self.parser.parse_args()


# for start in starts:
#     update_first = table.update_item(
#         Key={"_id": start["_id"]},
#         UpdateExpression="set #time=:t",
#         ExpressionAttributeValues={
#             ":t": Decimal(time.time()) - Decimal(86400000 / 1000) * Random().choice([1, 2, 3, 3])
#         },
#         ExpressionAttributeNames={
#             "#time": "time"
#         }
#     )
# if end is None:
#     oid = str(uuid.uuid4())
#     table.update_item(
#         Key={"_id": start["_id"]},
#         UpdateExpression="set event.orderId=:o",
#         ExpressionAttributeValues={
#             ":o": oid
#         }
#         # ExpressionAttributeNames={
#         #     "#time": "time"
#         # }
#     )
#
#     table.put_item(
#         Item={
#             '_id': str(uuid.uuid4()),
#             'time': Decimal(time.time()),
#             'type': 'arrived',
#             'event': {
#                 'driverId': 'D3A6E60BFECF4C4393F9EEFBC6E8D48C',
#                 'orderId': oid,
#                 'directions': [],
#                 'distance': 16,
#                 'duration': Decimal(1)
#             }
#         }
#     )
#     print(f"Updated {start} by creating order id {oid}")

def m_to_mi(m):
    return m / 1609.34


def ms_to_mph(speed):
    return speed * 2.23694


def get_table():
    load_dotenv(os.getenv('ENV_FILE') or '.env')
    dynamodb = boto3.resource('dynamodb',
                              endpoint_url="http://dynamodb.us-east-2.amazonaws.com",
                              aws_access_key_id=os.environ.get("AWS_ID"),
                              aws_secret_access_key=os.environ.get("AWS_KEY")
                              )
    return dynamodb.Table('metadata')


def get_end(start, items):
    if "orderId" not in start["event"] or "driverId" not in start["event"]:
        return None

    driver_id = start["event"]["driverId"]
    order_id = start["event"]["orderId"]
    for item in items:
        if (item["type"] == "arrived" and
                "orderId" in item["event"] and
                "driverId" in item["event"] and
                item["event"]["driverId"] == driver_id and
                item["event"]["orderId"] == order_id):
            return item


def plot_miles_per_day(starts):
    distances = {}
    for start in starts:
        time = datetime.fromtimestamp(int(start["time"]))
        timestamp = time.strftime('%m/%d/%Y')
        if timestamp not in distances:
            distances[timestamp] = 0.0
        if "distance" in start["event"]:
            distances[timestamp] += m_to_mi(float(start["event"]["distance"]))

    data = sorted(distances.items())
    plt.plot([x[0] for x in data],
             [x[1] for x in data])

    plt.xlabel("Date")
    plt.ylabel("Driver miles")
    plt.title("Total delivery miles per day")
    plt.show()


def plot_estimated_time_inaccuracy(starts, items):
    averages = {}
    for start in starts:
        end = get_end(start, items)
        if end is not None:
            expected = start["event"]["duration"]
            actual = end["time"] - start["time"]
            delta = expected - actual
            time = datetime.fromtimestamp(int(end["time"]))
            timestamp = time.strftime('%m/%d/%Y')
            if timestamp not in averages:
                averages[timestamp] = []
            averages[timestamp].append(delta)

    for key in averages:
        avgr = sum(averages[key]) / len(averages[key])
        averages[key] = avgr

    data = sorted(averages.items())
    plt.plot([x[0] for x in data],
             [x[1] for x in data])

    plt.xlabel("Date")
    plt.ylabel("Average inaccuracy (seconds)")
    plt.title("Average inaccuracy per day")
    plt.show()


def plot_mph_per_day(starts, items):
    real = {}
    expected = {}
    for start in starts:
        end = get_end(start, items)
        if end is not None:
            expected_speed = start["event"]["distance"] / start["event"]["duration"]
            actual = start["event"]["distance"] / (end["time"] - start["time"])

            time = datetime.fromtimestamp(int(end["time"]))
            timestamp = time.strftime('%m/%d/%Y')
            if timestamp not in real:
                real[timestamp] = []
                expected[timestamp] = []
            real[timestamp].append(actual)
            expected[timestamp].append(expected_speed)
    for key in expected:
        expected[key] = sum(expected[key]) / len(expected[key])
        real[key] = sum(real[key]) / len(real[key])

    expected_data = sorted(expected.items())
    real_data = sorted(real.items())
    plt.plot([x[0] for x in expected_data],
             [x[1] for x in expected_data])

    plt.plot([x[0] for x in real_data],
             [x[1] for x in real_data])

    plt.xlabel("Date")
    plt.ylabel("Average speed (mph)")
    plt.title("Average speed per day")
    plt.legend(['Expected', 'Actual'])
    plt.show()


def run():
    plt.style.use("fivethirtyeight")

    table = get_table()
    table_items = table.scan()
    items = table_items["Items"]

    user_args = vars(VisualizationArgParser().get_args())
    if user_args["driverId"] is not None:
        items = list(filter(lambda x: x["driverId"] == user_args["driverId"], items))
    if user_args["before"] is not None:
        items = list(filter(lambda x: x["time"] < user_args["before"].timestamp(), items))
    if user_args["after"] is not None:
        items = list(filter(lambda x: x["time"] > user_args["after"].timestamp(), items))

    starts = list(filter(lambda x: x["type"] == "start", items))
    if user_args["miles_per_day"]:
        plot_miles_per_day(starts)
    elif user_args["time_inaccuracy"]:
        plot_estimated_time_inaccuracy(starts, items)
    elif user_args["mph"]:
        plot_mph_per_day(starts, items)
    else:
        print("Include either --miles-per-day, --time-inaccuracy, or --mph to display a graph")


if __name__ == "__main__":
    run()
