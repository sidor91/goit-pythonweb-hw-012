from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

PHONE_REGEX = r"^\+\d{7,15}$"


class ContactBaseSchema(BaseModel):
    second_name: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    birthday: date | None = None
    additional_info: str | None = Field(default=None, max_length=250)

    @field_validator("second_name")
    @classmethod
    def validate_names(cls, v: str | None):
        if v is None:
            return v
        v = v.strip()
        return v or None

    @field_validator("birthday")
    @classmethod
    def validate_birthday(cls, v: date | None):
        if v is None:
            return v
        if v > date.today():
            raise ValueError("Birthday cannot be in the future")
        return v
    
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str | None):
        if v is None:
            return v
        return v.lower()


class ContactCreateSchema(ContactBaseSchema):
    first_name: str = Field(min_length=1, max_length=50)
    phone: str = Field(pattern=PHONE_REGEX)

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str):
        if not v.strip():
            raise ValueError("First name cannot be empty")
        return v.strip()

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, v: str | None):
        if v is None:
            return v
        v = v.replace(" ", "").replace("-", "")
        return v


class ContactUpdateSchema(ContactBaseSchema):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    phone: str | None = Field(default=None, pattern=PHONE_REGEX)

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str | None):
        if v is None:
            return v
        return v.strip()

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, v: str | None):
        if v is None:
            return v
        v = v.replace(" ", "").replace("-", "")
        return v


class ContactResponseSchema(ContactBaseSchema):
    id: int
    first_name: str
    phone: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
