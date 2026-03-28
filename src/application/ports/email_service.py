from abc import ABC, abstractmethod

class EmailService(ABC):

    @abstractmethod
    async def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str) -> bool:
        ...

    @abstractmethod
    async def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        ...

    @abstractmethod
    async def send_password_changed_email(self, to_email: str, user_name: str) -> bool:
        ...
