"""Create the database from db.sql and load the demo data, only if it is not there yet.

Run from backend/: python -m db.init_db
"""
import re
import time
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from db.db import engine
from db.seed_demo import seed_demo


def create_database_if_missing(url):
    master = create_engine(url.set(database="master"), isolation_level="AUTOCOMMIT")
    # SQL Server needs ~20s on the first container start before it accepts logins.
    for attempt in range(30):
        try:
            with master.connect() as conn:
                conn.exec_driver_sql(f"IF DB_ID(N'{url.database}') IS NULL CREATE DATABASE [{url.database}]")
            return
        except DBAPIError:
            if attempt == 29:
                raise
            print("SQL Server non ancora pronto, nuovo tentativo tra 2s...")
            time.sleep(2)


def main():
    create_database_if_missing(engine.url)
    with engine.begin() as conn:
        if conn.execute(text("SELECT SCHEMA_ID('core')")).scalar() is not None:
            print("Database già inizializzato.")
            return
        sql = (Path(__file__).parent / "db.sql").read_text(encoding="utf-8")
        for batch in re.split(r"^\s*GO\s*$", sql, flags=re.MULTILINE | re.IGNORECASE):
            if batch.strip():
                conn.exec_driver_sql(batch)
        seed_demo(Session(bind=conn))
    print("Database creato con i dati demo.")


if __name__ == "__main__":
    main()
