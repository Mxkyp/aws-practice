"""DELETE /shows/{id}/seasons/{n}: the season item and all its episodes.

Same contract as deleting an episode: always 204 with no body, 400 for a bad
season number.

The test builds its own season (show 82, season 98, not in the seed data and
not the season the episode test uses) with 30 episodes: more than one
BatchWriteItem call (max 25), so the chunking is really exercised.
"""

import pytest
from shows.keys import episode_sk, season_sk, show_pk

GOT = "/shows/82"
SEASON = 98
EPISODES = 30
THROWAWAY = f"{GOT}/seasons/{SEASON}"


@pytest.fixture
def throwaway_season(table):
    pk = show_pk(82)
    keys = [{"pk": pk, "sk": season_sk(SEASON)}] + [
        {"pk": pk, "sk": episode_sk(SEASON, e)} for e in range(1, EPISODES + 1)
    ]
    with table.batch_writer() as batch:
        batch.put_item(Item={**keys[0], "tvmaze_id": 0, "number": SEASON})
        for e, key in enumerate(keys[1:], start=1):
            batch.put_item(
                Item={**key, "tvmaze_id": 0, "season": SEASON, "number": e, "name": f"Throwaway {e}"}
            )
    yield THROWAWAY
    with table.batch_writer() as batch:  # in case the test failed midway
        for key in keys:
            batch.delete_item(Key=key)


def test_delete_season(get, delete, throwaway_season):
    assert get(throwaway_season).status == 200
    assert len(get(f"{throwaway_season}/episodes").body["episodes"]) == EPISODES

    r = delete(throwaway_season)
    assert r.status == 204
    assert r.body is None

    assert get(throwaway_season).status == 404
    assert get(f"{throwaway_season}/episodes").body == {"episodes": []}


def test_delete_missing_season_is_204(delete):
    assert delete(THROWAWAY).status == 204
    assert delete("/shows/999999/seasons/1").status == 204


@pytest.mark.parametrize("bad", ["abc", "0", "-1"])
def test_bad_season_number_is_400(delete, bad):
    assert delete(f"{GOT}/seasons/{bad}").status == 400
