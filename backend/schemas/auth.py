
from pydantic import BaseModel, EmailStr, Field
from datetime import date


# Data required when a user signs up
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    gender: str
    date_of_birth: date


# Data returned after signup
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    gender: str
    date_of_birth: date
    profile_picture: str | None = None

    model_config = {"from_attributes": True}


# Data required when a user logs in
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Data returned after successful login
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
