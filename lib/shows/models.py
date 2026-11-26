import dataclasses
import json
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _opt_int(value: Any) -> int | None:
    return int(value) if value is not None else None


def _opt_float(value: Any) -> float | None:
    return float(value) if value is not None else None


def _to_dict(obj: Any) -> dict[str, Any]:
    return {
        k: v.isoformat() if isinstance(v, date) else v
        for k, v in dataclasses.asdict(obj).items()
    }


@dataclass(frozen=True)
class ShowResponse:
    tvmaze_id: int
    name: str
    slug: str
    status: str
    premiered: date | None = None
    ended: date | None = None
    genres: list[str] = field(default_factory=list)
    rating: float | None = None
    summary: str | None = None  # HTML

    @classmethod
    def from_tvmaze(cls, data: dict[str, Any]) -> "ShowResponse":
        return cls(
            tvmaze_id=data["id"],
            name=data["name"],
            slug=data["url"].rsplit("/", 1)[-1],
            status=data["status"],
            premiered=_parse_date(data["premiered"]),
            ended=_parse_date(data["ended"]),
            genres=data["genres"],
            rating=(data.get("rating") or {}).get("average"),
            summary=data["summary"],
        )

    @classmethod
    def from_item(cls, item: dict[str, Any]) -> "ShowResponse":
        return cls(
            tvmaze_id=int(item["tvmaze_id"]),
            name=item["name"],
            slug=item["slug"],
            status=item["status"],
            premiered=_parse_date(item.get("premiered")),
            ended=_parse_date(item.get("ended")),
            genres=list(item.get("genres", [])),
            rating=_opt_float(item.get("rating")),
            summary=item.get("summary"),
        )

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass(frozen=True)
class SeasonResponse:
    tvmaze_id: int
    number: int
    name: str | None = None  # TVMaze often has "" here
    episode_order: int | None = None  # planned episode count
    premiered: date | None = None
    ended: date | None = None
    summary: str | None = None  # HTML

    @classmethod
    def from_tvmaze(cls, data: dict[str, Any]) -> "SeasonResponse":
        return cls(
            tvmaze_id=data["id"],
            number=data["number"],
            name=data["name"] or None,
            episode_order=data["episodeOrder"],
            premiered=_parse_date(data["premiereDate"]),
            ended=_parse_date(data["endDate"]),
            summary=data["summary"],
        )

    @classmethod
    def from_item(cls, item: dict[str, Any]) -> "SeasonResponse":
        return cls(
            tvmaze_id=int(item["tvmaze_id"]),
            number=int(item["number"]),
            name=item.get("name"),
            episode_order=_opt_int(item.get("episode_order")),
            premiered=_parse_date(item.get("premiered")),
            ended=_parse_date(item.get("ended")),
            summary=item.get("summary"),
        )

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


@dataclass(frozen=True)
class EpisodeResponse:
    tvmaze_id: int
    season: int
    number: int
    name: str
    airdate: date | None = None
    runtime: int | None = None  # minutes
    rating: float | None = None
    summary: str | None = None  # HTML

    @classmethod
    def from_tvmaze(cls, data: dict[str, Any]) -> "EpisodeResponse":
        return cls(
            tvmaze_id=data["id"],
            season=data["season"],
            number=data["number"],
            name=data["name"],
            airdate=_parse_date(data["airdate"]),
            runtime=data["runtime"],
            rating=(data.get("rating") or {}).get("average"),
            summary=data["summary"],
        )

    @classmethod
    def from_item(cls, item: dict[str, Any]) -> "EpisodeResponse":
        return cls(
            tvmaze_id=int(item["tvmaze_id"]),
            season=int(item["season"]),
            number=int(item["number"]),
            name=item["name"],
            airdate=_parse_date(item.get("airdate")),
            runtime=_opt_int(item.get("runtime")),
            rating=_opt_float(item.get("rating")),
            summary=item.get("summary"),
        )

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)
