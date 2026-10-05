import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """
    Yields a real DB session wrapped in a transaction that is always
    rolled back, so tests never leave data behind.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client():
    from main import app
    with TestClient(app) as c:
        # Authenticate against the API-key middleware when a key is configured.
        key = os.getenv("API_KEY", "").strip()
        if key:
            c.headers.update({"X-API-Key": key})
        yield c
