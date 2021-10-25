# Metadata lambda that is setup on AWS for processing messages and storing specific ones in DynamoDB
import base64
import json
import time
import uuid
from decimal import Decimal

import boto3

STORE_EVENTS = ["arrived", "start", "approach"]


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', endpoint_url="http://dynamodb.us-east-2.amazonaws.com")
    table = dynamodb.Table('metadata')

    for record in event['Records']:
        payload = base64.b64decode(record['kinesis']['data']).decode('utf-8')
        decoded = json.loads(payload, parse_float=Decimal)
        if (decoded["type"] in STORE_EVENTS):
            response = table.put_item(
                Item={
                    'type': decoded["type"],
                    'time': Decimal(time.time()),
                    '_id': str(uuid.uuid4()),
                    'event': decoded
                }
            )
