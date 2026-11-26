"""Key layout of the single `show` table. Every item of a show shares its pk.

    pk = SHOW#82   sk = META        the show
    pk = SHOW#82   sk = SEASON#01   season 1
    pk = SHOW#82   sk = S#01#E#03   season 1, episode 3

Seasons and episodes use different prefixes so each list is one contiguous
slice of the sort order: begins_with("SEASON#") reads only seasons, and
begins_with("S#01#E#") reads only that season's episodes.

Numbers are zero-padded so the string sort order matches the numeric order
(S#02 < S#10). Two digits cover the seed data (max 9 seasons, 28 episodes).
"""

SHOW_SK = "META"
SEASON_PREFIX = "SEASON#"


def show_pk(show_id: int | str) -> str:
    return f"SHOW#{show_id}"


def season_sk(season: int) -> str:
    return f"{SEASON_PREFIX}{season:02d}"


def episode_prefix(season: int) -> str:
    return f"S#{season:02d}#E#"


def episode_sk(season: int, episode: int) -> str:
    return f"{episode_prefix(season)}{episode:02d}"
