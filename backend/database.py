from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from urllib.parse import quote_plus
from core.config import settings

# Database URL
DATABASE_URL = (
    f"mysql+pymysql://{settings.DB_USER}:"
    f"{quote_plus(settings.DB_PASSWORD)}@"
    f"{settings.DB_HOST}:"
    f"{settings.DB_PORT}/"
    f"{settings.DB_NAME}"
)

# Create SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    echo=True
)

# Create Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all database models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
