from pydantic import BaseModel, EmailStr, Field, field_validator, AfterValidator
from typing import Annotated
import re


def validate_username(value: str) -> str:
    if not re.fullmatch(r"[a-zA-Z0-9_]+", value):
        raise ValueError("Username can contain only letters, digits, and underscores")
    if len(re.findall(r"[a-zA-Z]", value)) < 3:
        raise ValueError("Username must contain at least 3 letters")

    return value

Username = Annotated[
    str,
    Field(min_length=3, max_length=20),
    AfterValidator(validate_username)
]

class LoginUser(BaseModel):
    email: EmailStr
    password: str 

class RegisterUser(LoginUser):
    username: Username
    password: str = Field(min_length=8, max_length=32)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain one or more digits")

        return value