import json
import os

import boto3

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    slug = event["show"]
    item = table.get_item(Key={"pk": slug, "sk": "META"}).get("Item")
    if item is None:
        return {"statusCode": 404, "body": json.dumps({"error": f"no show '{slug}'"})}
    return {"statusCode": 200, "body": json.dumps(item, default=str)}
