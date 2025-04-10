from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactBase

from sqlalchemy.sql.expression import and_, extract, or_

from datetime import date, timedelta


class ContactRepository:
    def __init__(self, session: AsyncSession):
        # Store the asynchronous database session
        self.db = session

    async def get_contacts(
        self,
        skip: int = 0,
        limit: int = 10,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> List[Contact]:
        filters = []

        # Add filters based on the provided query parameters
        if first_name:
            filters.append(Contact.first_name.like(f"%{first_name}%"))
        if last_name:
            filters.append(Contact.last_name.like(f"%{last_name}%"))
        if email:
            filters.append(Contact.email.like(f"%{email}%"))

        # Construct and execute the SELECT statement with dynamic filtering, pagination
        stmt = select(Contact).where(and_(*filters)).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)

        # Return the list of matched contacts
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        # Retrieve a single contact by its ID
        stmt = select(Contact).filter_by(id=contact_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_contact(self, body: ContactBase) -> Contact:
        # Create a new Contact object from validated request data
        contact = Contact(**body.model_dump(exclude_unset=True))
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)  # Load updated state from the database
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactBase
    ) -> Contact | None:
        # Retrieve the existing contact and update its fields
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            contact.first_name = body.first_name
            contact.last_name = body.last_name
            contact.birthday = body.birthday
            contact.additional_info = body.additional_info
            contact.email = body.email
            contact.phone_number = body.phone_number

            await self.db.commit()
            await self.db.refresh(contact)  # Get the latest data after commit
        return contact

    async def remove_contact(self, contact_id: int) -> Contact | None:
        # Delete a contact by its ID if it exists
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def get_upcoming_birthdays(self, days: int = 7) -> List:
        # Find contacts with birthdays in the next `days` number of days
        today = date.today()
        target_date = today + timedelta(days=days)

        if target_date.year == today.year:
            # Case when the range stays within the same calendar year
            stmt = select(Contact).filter(
                or_(
                    # Birthdays later this month
                    and_(
                        extract("month", Contact.birthday) == today.month,
                        extract("day", Contact.birthday) >= today.day,
                    ),
                    # Birthdays early in the target month
                    and_(
                        extract("month", Contact.birthday) == target_date.month,
                        extract("day", Contact.birthday) <= target_date.day,
                    ),
                    # Birthdays in full months between today and the target date
                    and_(
                        extract("month", Contact.birthday) > today.month,
                        extract("month", Contact.birthday) < target_date.month,
                    ),
                )
            )
        else:
            # Case when the range spans across the new year
            stmt = select(Contact).filter(
                or_(
                    # Birthdays later this year
                    and_(
                        extract("month", Contact.birthday) == today.month,
                        extract("day", Contact.birthday) >= today.day,
                    ),
                    and_(
                        extract("month", Contact.birthday) > today.month,
                    ),
                    # Birthdays early next year
                    and_(
                        extract("month", Contact.birthday) == target_date.month,
                        extract("day", Contact.birthday) <= target_date.day,
                    ),
                    and_(
                        extract("month", Contact.birthday) < target_date.month,
                    ),
                )
            )

        # Execute query and return the results
        result = await self.db.execute(stmt)
        return result.scalars().all()
