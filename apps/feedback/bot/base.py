from abc import ABC, abstractmethod

from apps.feedback.bot.utils.message import SingleMessage


class BaseBot(ABC):
    """Abstract class for messenger bots."""

    def __init__(self, token: str) -> None:
        self.token = token

    @abstractmethod
    async def send_message(self, message: SingleMessage, user_id: int) -> None:
        """Send message by user id.

        Args:
            message (SingleMessage): Message to send.
            user_id (int): User id from messenger.
        """
