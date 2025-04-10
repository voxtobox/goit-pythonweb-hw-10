from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class ContactBase(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone_number: str
    birthday: date
    additional_info: Optional[str]


class ContactUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]
    birthday: Optional[date]
    additional_info: Optional[str]


class ContactResponse(ContactBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
