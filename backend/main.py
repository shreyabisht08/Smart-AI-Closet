from fastapi import FastAPI
from sqlalchemy import text

from database import Base, engine
from models.user import User
from api.auth import router as auth_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StyleMind AI API",
    version="1.0.0"
)
app.include_router(auth_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to StyleMind AI 🚀"
    }


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": str(e)
        }