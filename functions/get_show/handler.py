import os

import boto3
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from shows.models import ShowResponse

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
app = APIGatewayRestResolver()


@app.get("/shows/<show_id>")
def get_show(show_id: str):
    item = table.get_item(Key={"pk": f"SHOW#{show_id}", "sk": "META"}).get("Item")
    if item is None:
        raise NotFoundError(f"no show with id {show_id}")
    return ShowResponse.from_item(item).to_dict()


def lambda_handler(event, context):
    return app.resolve(event, context)
