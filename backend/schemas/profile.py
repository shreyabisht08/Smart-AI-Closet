
from pydantic import BaseModel, Field
from datetime import date


class UserProfileUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    gender: str | None = None

    date_of_birth: date | None = None


class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    gender: str
    date_of_birth: date
    profile_picture: str | None = None

    model_config = {"from_attributes": True}
