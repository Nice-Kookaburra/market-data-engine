from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DataSource:
    name: str
    provider: str
    api_key_ref: str | None = None
    rate_limits: dict[str, Any] = field(default_factory=dict)