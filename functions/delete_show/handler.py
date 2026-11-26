import os

import boto3
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from shows.keys import episode_sk, show_pk
from shows.params import parse_number

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
app = APIGatewayRestResolver()


@app.delete("/shows/<show_id>/seasons/<season>/episodes/<episode>")
def delete_episode(show_id: str, season: str, episode: str):
    s, e = parse_number(season, "season"), parse_number(episode, "episode")
    # Idempotent: DeleteItem succeeds whether or not the item existed, and the
    # API says the same. "After this call the episode is gone" is the contract.
    table.delete_item(Key={"pk": show_pk(show_id), "sk": episode_sk(s, e)})
    return Response(status_code=204)


def lambda_handler(event, context):
    return app.resolve(event, context)
