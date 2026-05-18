from dataclasses import dataclass
from datetime import date
from typing import Literal


CorporateActionType = Literal["split", "dividend"]


@dataclass(frozen=True)
class CorporateAction:
    asset_id: str
    action_type: CorporateActionType
    day: date
    value: float