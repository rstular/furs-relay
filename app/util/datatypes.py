from dataclasses import dataclass
from typing import Optional


@dataclass
class ActionResponse:
    success: bool
    message: Optional[str] = None
