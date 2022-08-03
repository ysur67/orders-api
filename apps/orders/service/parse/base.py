from abc import ABC, abstractmethod


class BaseParser(ABC):

    @abstractmethod
    def parse(self) -> None:
        return

    def set_up(self) -> None:
        return
