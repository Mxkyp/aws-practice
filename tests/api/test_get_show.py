"""GET routes of the shows API, checked against the committed seed data.

Show 82 is Game of Thrones: 8 seasons, season 1 has 10 episodes.
Show 999999 does not exist.
"""

from urllib.parse import quote

import pytest

GOT = "/shows/82"
MISSING = "/shows/999999"


# --- 200: one happy path per route -----------------------------------------


def test_get_show(get):
    r = get(GOT)
    assert r.status == 200
    assert r.body["name"] == "Game of Thrones"
    assert r.body["rating"] == 8.9  # Decimal from DynamoDB came out as a number


def test_list_seasons(get):
    r = get(f"{GOT}/seasons")
    assert r.status == 200
    assert [s["number"] for s in r.body["seasons"]] == list(range(1, 9))


def test_get_season(get):
    r = get(f"{GOT}/seasons/1")
    assert r.status == 200
    assert r.body["number"] == 1


def test_list_episodes(get):
    r = get(f"{GOT}/seasons/1/episodes")
    assert r.status == 200
    assert [e["number"] for e in r.body["episodes"]] == list(range(1, 11))


def test_get_episode(get):
    r = get(f"{GOT}/seasons/1/episodes/1")
    assert r.status == 200
    assert r.body["name"] == "Winter is Coming"


# --- lists: nothing found is an empty list, not a 404 -----------------------


@pytest.mark.parametrize(
    ("path", "key"),
    [
        (f"{MISSING}/seasons", "seasons"),
        (f"{GOT}/seasons/9/episodes", "episodes"),
    ],
)
def test_list_of_nothing_is_empty(get, path, key):
    r = get(path)
    assert r.status == 200
    assert r.body == {key: []}


# --- 404: a single item that does not exist ---------------------------------


@pytest.mark.parametrize(
    "path",
    [
        MISSING,
        f"{GOT}/seasons/9",
        f"{GOT}/seasons/1/episodes/11",
    ],
)
def test_missing_item_is_404(get, path):
    assert get(path).status == 404


# --- 400: season/episode segments that are not positive integers ------------

BAD_NUMBERS = [
    "abc",  # not a number at all
    "0",  # numeric but not positive: there is no season 0
    "00",  # same, but slips past a naive `raw == "0"` check
    "-1",  # sign is not a decimal digit
    "1.5",  # not an integer
    "²",  # isdigit() is True, int() raises: the old 500
]


@pytest.mark.parametrize("bad", BAD_NUMBERS)
def test_bad_season_number_is_400(get, bad):
    # quote(): URLs are ASCII on the wire, so "²" travels as %C2%B2.
    # aws-emulator hands pathParameters to the Lambda still encoded, so on the
    # emulator this case hits the handler as "%C2%B2", not "²" — the isdecimal
    # fix is only exercised where API Gateway decodes the segment.
    assert get(f"{GOT}/seasons/{quote(bad)}").status == 400


def test_leading_zero_is_accepted(get):
    """Deliberate contract: "01" means season 1, like the zero-padded keys."""
    r = get(f"{GOT}/seasons/01")
    assert r.status == 200
    assert r.body["number"] == 1
