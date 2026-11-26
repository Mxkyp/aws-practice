import os

import boto3
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from boto3.dynamodb.conditions import Key
from shows.keys import episode_prefix, episode_sk, season_sk, show_pk
from shows.params import parse_number

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
app = APIGatewayRestResolver()


def _keys_with_prefix(pk: str, prefix: str) -> list[dict]:
    """Keys (pk, sk only) of every item under pk whose sk starts with prefix.

    Follows LastEvaluatedKey: one Query page stops at 1 MB.
    """
    kwargs = {
        "KeyConditionExpression": Key("pk").eq(pk) & Key("sk").begins_with(prefix),
        "ProjectionExpression": "pk, sk",
    }
    keys = []
    while True:
        resp = table.query(**kwargs)
        keys.extend(resp["Items"])
        if "LastEvaluatedKey" not in resp:
            return keys
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]


@app.delete("/shows/<show_id>/seasons/<season>")
def delete_season(show_id: str, season: str):
    n = parse_number(season, "season")
    pk = show_pk(show_id)

    # Episodes first. batch_writer sends deletes in chunks of 25 and resends
    # UnprocessedItems; leaving the `with` block means every one was accepted.
    with table.batch_writer() as batch:
        for key in _keys_with_prefix(pk, episode_prefix(n)):
            batch.delete_item(Key=key)

    # Season item last, outside the batch (a batch has no order guarantee).
    # If the Lambda dies above, the season is still listed and a retried
    # DELETE finishes the job.
    table.delete_item(Key={"pk": pk, "sk": season_sk(n)})
    return Response(status_code=204)


@app.delete("/shows/<show_id>/seasons/<season>/episodes/<episode>")
def delete_episode(show_id: str, season: str, episode: str):
    s, e = parse_number(season, "season"), parse_number(episode, "episode")
    # Idempotent: DeleteItem succeeds whether or not the item existed, and the
    # API says the same. "After this call the episode is gone" is the contract.
    table.delete_item(Key={"pk": show_pk(show_id), "sk": episode_sk(s, e)})
    return Response(status_code=204)


def lambda_handler(event, context):
    return app.resolve(event, context)
