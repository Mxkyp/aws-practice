"""DELETE /shows/{id}: the show item, all its seasons and all their episodes.

Same contract as the other deletes: always 204 with no body.

The test builds its own show (999998, not in the seed data) with 2 seasons of
15 episodes: 33 items, so more than one BatchWriteItem call (max 25).
"""

import pytest
from shows.keys import SHOW_SK, episode_sk, season_sk, show_pk

SHOW_ID = 999998
SEASONS = 2
EPISODES = 15
THROWAWAY = f"/shows/{SHOW_ID}"


@pytest.fixture
def throwaway_show(table):
    pk = show_pk(SHOW_ID)
    items = [
        {"sk": SHOW_SK, "tvmaze_id": SHOW_ID, "name": "Throwaway", "slug": "throwaway", "status": "Ended"}
    ]
    for s in range(1, SEASONS + 1):
        items.append({"sk": season_sk(s), "tvmaze_id": 0, "number": s})
        items += [
            {"sk": episode_sk(s, e), "tvmaze_id": 0, "season": s, "number": e, "name": f"Throwaway {e}"}
            for e in range(1, EPISODES + 1)
        ]
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item={"pk": pk, **item})
    yield THROWAWAY
    with table.batch_writer() as batch:  # in case the test failed midway
        for item in items:
            batch.delete_item(Key={"pk": pk, "sk": item["sk"]})


def test_delete_show(get, delete, throwaway_show):
    assert get(throwaway_show).status == 200
    assert len(get(f"{throwaway_show}/seasons").body["seasons"]) == SEASONS

    r = delete(throwaway_show)
    assert r.status == 204
    assert r.body is None

    assert get(throwaway_show).status == 404
    assert get(f"{throwaway_show}/seasons").body == {"seasons": []}
    for s in range(1, SEASONS + 1):
        assert get(f"{throwaway_show}/seasons/{s}/episodes").body == {"episodes": []}


def test_delete_missing_show_is_204(delete):
    assert delete("/shows/999999").status == 204
