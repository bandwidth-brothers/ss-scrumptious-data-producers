import json

from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext

from app.driverStreaming.mapping import DriverDirectionHandler, get_api_key
from app.stream import StreamBuilder, set_spark_env

set_spark_env()
api_key = get_api_key()


def handle_message(message: str):
    direction_handler = DriverDirectionHandler(api_key)
    data = json.loads(message)
    direction_handler.handle_message(data)


def run():
    stream_builder = StreamBuilder("driver-directions")

    spark = SparkSession \
        .builder \
        .appName("driverDirectionsStreaming") \
        .getOrCreate()

    ssc = StreamingContext(spark.sparkContext, 1)

    kinesis = stream_builder.get_spark_stream(ssc)

    kinesis.foreachRDD(lambda data: data.foreach(handle_message))
    ssc.start()
    ssc.awaitTermination()


if __name__ == "__main__":
    run()
