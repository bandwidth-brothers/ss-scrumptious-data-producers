import os

import boto3
from botocore.client import BaseClient
from dotenv import load_dotenv
from pyspark import StorageLevel
from pyspark.sql.streaming import DataStreamWriter
from pyspark.streaming import StreamingContext, DStream
from pyspark.streaming.kinesis import KinesisUtils, InitialPositionInStream


def set_spark_env():
    os.environ[
        'PYSPARK_SUBMIT_ARGS'] = "--packages=org.apache.spark:spark-streaming-kinesis-asl_2.12:3.1.2,com.qubole.spark:spark-sql-kinesis_2.12:1.2.0_spark-3.0 pyspark-shell"


class StreamBuilder:
    def __init__(self, stream_name):
        load_dotenv(os.getenv('ENV_FILE') or '.env')

        self.db_user = os.environ.get('DATABASE_USERNAME')
        self.stream_name = stream_name  # "driver-directions"
        self.stream_url = "https://kinesis.us-east-2.amazonaws.com"
        self.region_name = "us-east-2"
        self.aws_id = os.environ.get("AWS_ID")
        self.aws_key = os.environ.get("AWS_KEY")

    def get_spark_stream(self, ssc: StreamingContext) -> DStream:
        return KinesisUtils.createStream(ssc, ssc.sparkContext.appName, self.stream_name,
                                         self.stream_url,
                                         self.region_name,
                                         InitialPositionInStream.LATEST, 2, StorageLevel.MEMORY_AND_DISK_2,
                                         self.aws_id,
                                         self.aws_key)

    def get_stream(self) -> BaseClient:
        return boto3.client("kinesis", aws_access_key_id=self.aws_id, aws_secret_access_key=self.aws_key,
                            region_name=self.region_name)

    def set_options(self, stream: DataStreamWriter) -> DataStreamWriter:
        return stream.option("streamName", self.stream_name) \
            .option("endpointUrl", self.stream_url) \
            .option("awsAccessKeyId", self.aws_id) \
            .option("awsSecretKey", self.aws_key) \
            .option("checkpointLocation", "tmp/checkpoint")
