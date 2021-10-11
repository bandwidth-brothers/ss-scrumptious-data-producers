import json
from time import sleep

from app.stream import StreamBuilder


def create_test_data(path: str):
    stream_builder = StreamBuilder("driver-directions")
    kinesis = stream_builder.get_stream()

    with open(path) as file:
        data = json.load(file)
        for entry in data:
            kinesis.put_record(StreamName=stream_builder.stream_name, Data=json.dumps(entry),
                               PartitionKey=stream_builder.stream_name)


def run():
    while True:
        create_test_data("app/data/driverUpdates.json")
        print("Added data to stream!")
        sleep(1)


if __name__ == "__main__":
    run()
