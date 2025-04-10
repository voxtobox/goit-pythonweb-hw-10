from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactBase


class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase):
        return await self.repository.create_contact(body)

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        first_name: str | None,
        last_name: str | None,
        email: str | None,
    ):
        return await self.repository.get_contacts(
            skip, limit, first_name, last_name, email
        )

    async def get_contact(self, contact: int):
        return await self.repository.get_contact_by_id(contact)

    async def update_contact(self, contact: int, body: ContactBase):
        return await self.repository.update_contact(contact, body)

    async def remove_contact(self, contact: int):
        return await self.repository.remove_contact(contact)

    async def upcoming_birthdays(self, days: int):
        return await self.repository.get_upcoming_birthdays(days)
