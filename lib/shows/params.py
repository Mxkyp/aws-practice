"""Parsing of URL path parameters shared by the API handlers."""

from aws_lambda_powertools.event_handler.exceptions import BadRequestError


def parse_number(raw: str, what: str) -> int:
    """Season/episode segment -> positive int, or a 400 response."""
    if not raw.isdecimal() or int(raw) == 0:
        raise BadRequestError(f"{what} must be a positive integer, got {raw!r}")
    return int(raw)
