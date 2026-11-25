from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
    Boolean
)
from datetime import datetime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False, index=True)

    password = Column(String(255), nullable=False)

    gender = Column(String(20), nullable=False)

    date_of_birth = Column(Date, nullable=False)

    profile_picture = Column(String(500), nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )