from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


SQLALCHEMY_DATABASE_URL = settings.get_db_url()
is_sqlite = SQLALCHEMY_DATABASE_URL.startswith("sqlite")

engine_kwargs: dict = {"pool_pre_ping": True}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = settings.SQLALCHEMY_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.SQLALCHEMY_MAX_OVERFLOW
    engine_kwargs["pool_recycle"] = settings.SQLALCHEMY_POOL_RECYCLE

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
