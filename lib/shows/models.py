import dataclasses
import json
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


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
        rating = item.get("rating")
        return cls(
            tvmaze_id=int(item["tvmaze_id"]),
            name=item["name"],
            slug=item["slug"],
            status=item["status"],
            premiered=_parse_date(item.get("premiered")),
            ended=_parse_date(item.get("ended")),
            genres=list(item.get("genres", [])),
            rating=float(rating) if rating is not None else None,
            summary=item.get("summary"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            k: v.isoformat() if isinstance(v, date) else v
            for k, v in dataclasses.asdict(self).items()
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
