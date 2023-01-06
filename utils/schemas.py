import phonenumbers
from uuid import UUID
from typing import Dict
from pydantic import BaseModel, Field, EmailStr
from pydantic.validators import strict_str_validator
from fastapi import HTTPException, status


class PhoneNumber(str):

    @classmethod
    def __get_validators__(cls):
        yield strict_str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: str):
        v = v.strip().replace(' ', '')

        try:
            pn = phonenumbers.parse(v)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format"
            )

        return cls(phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164))


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class UserAuth(BaseModel):
    first_name: str = Field(..., description="user first name")
    last_name: str = Field(..., description="user last name")
    phone_number: PhoneNumber = Field(..., description="user phone number")
    email: EmailStr = Field(..., format='email', description="user email")
    password: str = Field(..., min_length=5, max_length=24,
                          description="user password")


class UserOut(BaseModel):
    first_name: str
    last_name: str
    _id: UUID
    email: EmailStr
    phone_number: PhoneNumber


class SystemUser(UserOut):
    email: str
    password: str


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, description="product name")
    description: str = Field(..., min_length=1,
                             description="product description")
    price: float = Field(..., gt=0.01, description="product price")
    weight: float = Field(..., gt=0.001, description="product weight")
    category: str


class ProductUpdate(BaseModel):
    name: str = Field(..., min_length=1, description="product name")
    description: str = Field(..., min_length=1,
                             description="product description")
    price: float = Field(..., gt=0.01, description="product price")
    weight: float = Field(..., gt=0.001, description="product weight")
    category: str


class StatusList(BaseModel):
    name: str


class NewOrder(BaseModel):
    email: EmailStr = Field(..., format='email', description="user email")
    phone_number: PhoneNumber
    ordered_products: Dict[str, int]
