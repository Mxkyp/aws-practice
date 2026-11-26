"""DELETE /shows/{id}/seasons/{n}/episodes/{m}.

Contract: always 204 with no body, whether or not the episode existed
(idempotent delete). Bad season/episode numbers are still 400.

The test creates its own episode (show 82, season 99, never in the seed data)
so it doesn't touch the items the GET tests rely on, and can run repeatedly.
"""

import pytest
from shows.keys import episode_sk, show_pk

GOT = "/shows/82"
THROWAWAY = f"{GOT}/seasons/99/episodes/1"


@pytest.fixture
def throwaway_episode(table):
    key = {"pk": show_pk(82), "sk": episode_sk(99, 1)}
    table.put_item(
        Item={**key, "tvmaze_id": 0, "season": 99, "number": 1, "name": "Throwaway"}
    )
    yield THROWAWAY
    table.delete_item(Key=key)  # in case the test failed before deleting it


def test_delete_episode(get, delete, throwaway_episode):
    assert get(throwaway_episode).status == 200

    r = delete(throwaway_episode)
    assert r.status == 204
    assert r.body is None

    assert get(throwaway_episode).status == 404


def test_delete_missing_episode_is_204(delete):
    assert delete(THROWAWAY).status == 204
    assert delete("/shows/999999/seasons/1/episodes/1").status == 204


@pytest.mark.parametrize("bad", ["abc", "0", "-1"])
def test_bad_episode_number_is_400(delete, bad):
    assert delete(f"{GOT}/seasons/1/episodes/{bad}").status == 400
