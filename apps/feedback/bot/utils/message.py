from dataclasses import dataclass
from typing import Any


@dataclass
class SingleMessage:
    message: str

    def to_dict(self) -> 'dict[str, Any]':
        return {
            "message": self.message,
        }
