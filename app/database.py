from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

URL_DATABASE = (
    f"postgresql://"
    f"{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.DATABASE_PORT}/"
    f"{settings.POSTGRES_DB}"
)

engine = create_engine(URL_DATABASE, echo=True)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()