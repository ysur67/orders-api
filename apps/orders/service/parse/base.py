from abc import ABC, abstractmethod


class BaseParser(ABC):
    """Abstract class for Order parsers"""

    @abstractmethod
    def parse(self) -> None:
        """Starts the actual parsing of orders."""

    def set_up(self) -> None:
        """Sets up the parser.

        `Must be called before the parse method.`
        """
