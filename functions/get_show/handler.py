import json
import os
from http import HTTPStatus

import boto3
from shows.models import ShowResponse

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    show_id = event["id"]
    item = table.get_item(Key={"pk": f"SHOW#{show_id}", "sk": "META"}).get("Item")
    if item is None:
        return {
            "statusCode": HTTPStatus.NOT_FOUND,
            "body": json.dumps({"error": f"no show with id {show_id}"}),
        }
    show = ShowResponse.from_item(item)
    return {"statusCode": HTTPStatus.OK, "body": show.to_json()}
