from dataclasses import dataclass
from typing import Optional


@dataclass
class Command:
    goto: str
    update: Optional[dict] = None