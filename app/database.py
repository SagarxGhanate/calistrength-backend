from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # auto-reconnect if MySQL drops the connection
    pool_recycle=3600,        # recycle connections every hour
    echo=(settings.ENVIRONMENT == "development"),  # log SQL in dev only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
