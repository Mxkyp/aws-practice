import os

import boto3
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from boto3.dynamodb.conditions import Key
from shows.keys import (
    SEASON_PREFIX,
    SHOW_SK,
    episode_prefix,
    episode_sk,
    season_sk,
    show_pk,
)
from shows.models import EpisodeResponse, SeasonResponse, ShowResponse
from shows.params import parse_number as _number

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
app = APIGatewayRestResolver()


def _get(pk: str, sk: str, not_found: str) -> dict:
    item = table.get_item(Key={"pk": pk, "sk": sk}).get("Item")
    if item is None:
        raise NotFoundError(not_found)
    return item


@app.get("/shows/<show_id>")
def get_show(show_id: str):
    item = _get(show_pk(show_id), SHOW_SK, f"no show with id {show_id}")
    return ShowResponse.from_item(item).to_dict()


@app.get("/shows/<show_id>/seasons")
def list_seasons(show_id: str):
    resp = table.query(
        KeyConditionExpression=Key("pk").eq(show_pk(show_id))
        & Key("sk").begins_with(SEASON_PREFIX)
    )
    return {"seasons": [SeasonResponse.from_item(i).to_dict() for i in resp["Items"]]}


@app.get("/shows/<show_id>/seasons/<season>")
def get_season(show_id: str, season: str):
    n = _number(season, "season")
    item = _get(show_pk(show_id), season_sk(n), f"no season {n} for show {show_id}")
    return SeasonResponse.from_item(item).to_dict()


@app.get("/shows/<show_id>/seasons/<season>/episodes")
def list_episodes(show_id: str, season: str):
    n = _number(season, "season")
    resp = table.query(
        KeyConditionExpression=Key("pk").eq(show_pk(show_id))
        & Key("sk").begins_with(episode_prefix(n))
    )
    return {"episodes": [EpisodeResponse.from_item(i).to_dict() for i in resp["Items"]]}


@app.get("/shows/<show_id>/seasons/<season>/episodes/<episode>")
def get_episode(show_id: str, season: str, episode: str):
    s, e = _number(season, "season"), _number(episode, "episode")
    item = _get(
        show_pk(show_id),
        episode_sk(s, e),
        f"no episode S{s:02d}E{e:02d} for show {show_id}",
    )
    return EpisodeResponse.from_item(item).to_dict()


def lambda_handler(event, context):
    return app.resolve(event, context)
