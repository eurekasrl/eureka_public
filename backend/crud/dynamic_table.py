from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from sqlalchemy import inspect, text, MetaData, Table, Column, String, Integer, Date, Boolean, DateTime, DECIMAL, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from db.db import engine
from schemas.config import SCHEMA_MAPPING

def get_all_table_names(schema: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Returns a list of all table names in the database, optionally filtered by schema.
    Each item in the list is a dict with 'name' and 'schema'.
    """
    inspector = inspect(engine.connect())
    all_schemas = inspector.get_schema_names()
    table_names = []

    for s in all_schemas:
        if schema and s != schema:
            continue
        tables = inspector.get_table_names(schema=s)
        for table_name in tables:
            table_names.append({"name": table_name, "schema": s})
    return sorted(table_names, key=lambda x: (x['schema'], x['name']))

def get_table_schema(table_name: str, schema_name: str) -> List[Dict[str, Any]]:
    """
    Returns the schema (column names and types) for a given table.
    Includes FK constraint metadata so the frontend can resolve IDs to labels.
    """
    inspector = inspect(engine.connect())
    columns_info = inspector.get_columns(table_name, schema=schema_name)
    pk_constraint = inspector.get_pk_constraint(table_name, schema=schema_name)
    pk_cols = set(pk_constraint.get('constrained_columns', []))

    # Build a map: constrained_column -> FK info
    fk_map: Dict[str, Dict] = {}
    try:
        fks = inspector.get_foreign_keys(table_name, schema=schema_name)
        for fk in fks:
            for col in fk.get('constrained_columns', []):
                fk_map[col] = {
                    "referred_schema": fk.get('referred_schema', schema_name),
                    "referred_table": fk.get('referred_table'),
                    "referred_column": fk.get('referred_columns', ['id'])[0],
                    # Heuristic: prefer 'nome' column as display label, fall back to 'id'
                    "label_column": _guess_label_column(fk.get('referred_table', '')),
                }
    except Exception:
        pass  # FK inspection is best-effort; table still returns without it

    schema = []
    for col in columns_info:
        type_str = str(col['type'])
        if 'VARCHAR' in type_str.upper() or 'NVARCHAR' in type_str.upper():
            type_str = 'string'
        elif 'INT' in type_str.upper():
            type_str = 'integer'
        elif 'DECIMAL' in type_str.upper() or 'NUMERIC' in type_str.upper():
            type_str = 'number'
        elif 'DATE' in type_str.upper():
            type_str = 'date'
        elif 'TIME' in type_str.upper():
            type_str = 'datetime'
        elif 'BOOLEAN' in type_str.upper() or 'BIT' in type_str.upper():
            type_str = 'boolean'
        elif 'UNIQUEIDENTIFIER' in type_str.upper() or 'UUID' in type_str.upper():
            type_str = 'string (UUID)'

        entry: Dict[str, Any] = {
            "name": col['name'],
            "type": type_str,
            "primary_key": col['name'] in pk_cols,
            "nullable": col.get('nullable', True),
            "default": col.get('default'),
            "autoincrement": col.get('autoincrement', False),
        }
        if col['name'] in fk_map:
            entry["fk"] = fk_map[col['name']]

        schema.append(entry)
    return schema


# Columns considered good display labels, in priority order
_LABEL_CANDIDATES = ['nome', 'denominazione', 'cognome', 'descrizione', 'titolo', 'name']


def _guess_label_column(referred_table: str) -> str:
    """Return the most likely human-readable column name for a referenced table."""
    try:
        inspector = inspect(engine.connect())
        # Try to find the table in any schema
        for schema_name in inspector.get_schema_names():
            try:
                cols = [c['name'] for c in inspector.get_columns(referred_table, schema=schema_name)]
                for candidate in _LABEL_CANDIDATES:
                    if candidate in cols:
                        return candidate
                break
            except Exception:
                continue
    except Exception:
        pass
    return 'id'

def get_table_data(table_name: str, schema_name: str, skip: int = 0, limit: int = 100, parsed_filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Retrieves data from a specified table with optional filtering.
    """
    metadata = MetaData(schema=schema_name)
    table = Table(table_name, metadata, autoload_with=engine)
    pk_col = list(table.primary_key.columns)[0]  # first PK column
    stmt = table.select().order_by(pk_col).offset(skip).limit(limit)

    if parsed_filters:
        conditions = []
        for column_name, value in parsed_filters.items():
            if column_name in table.columns:
                conditions.append(table.columns[column_name] == value)
            else:
                raise ValueError(f"Filter column '{column_name}' not found in table '{schema_name}.{table_name}'.")
        if conditions:
            stmt = stmt.where(and_(*conditions))
    try:
        with engine.connect() as conn:
            result = conn.execute(stmt)
            return [dict(r._mapping) for r in result]
    except SQLAlchemyError as e:
        raise e

def _get_table_object(table_name: str, schema_name: str) -> Table:
    metadata = MetaData(schema=schema_name)
    return Table(table_name, metadata, autoload_with=engine)

def add_table_row(db: Session, table_name: str, schema_name: str, row_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adds a new row to a given table.
    Assumes row_data keys match column names.
    """
    pydantic_model = SCHEMA_MAPPING[schema_name][table_name]['create']
    validated_obj = pydantic_model.model_validate(row_data)
    clean_data = validated_obj.model_dump(exclude_unset=True)
    table = _get_table_object(table_name, schema_name)
    stmt = table.insert().values(clean_data)
    try:
        result = db.execute(stmt)
        db.commit()
        if result.inserted_primary_key:
            return {**row_data, "id": str(result.inserted_primary_key[0])} if 'id' not in row_data else row_data
        return row_data
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def update_table_row(db: Session, table_name: str, schema_name: str, primary_key_value: Any, row_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates an existing row in a given table based on its primary key.
    Assumes row_data keys match column names.
    """
    table = _get_table_object(table_name, schema_name)
    pk_column = None
    for col in table.primary_key.columns:
        pk_column = col # Assuming single primary key for simplicity in this proto

    if pk_column is None:
        raise ValueError(f"Table '{table_name}' in schema '{schema_name}' has no primary key defined or detectable.")

    # Remove the primary key from update data if present, as it's used in WHERE clause
    update_data = {k: v for k, v in row_data.items() if k != pk_column.name}

    if "updated_at" in table.c:
        update_data['updated_at'] = datetime.now(timezone.utc)
    stmt = table.update().where(pk_column == primary_key_value).values(update_data)
    try:
        result = db.execute(stmt)
        db.commit()
        if result.rowcount == 0:
            raise ValueError(f"No row found with primary key '{primary_key_value}' to update.")
        return {**row_data, pk_column.name: primary_key_value}
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def delete_table_row(db: Session, table_name: str, schema_name: str, primary_key_value: Any):
    """
    Deletes a row from a given table based on its primary key.
    """
    table = _get_table_object( table_name, schema_name)
    pk_column = None
    for col in table.primary_key.columns:
        pk_column = col # Assuming single primary key for simplicity

    if pk_column is None:
        raise ValueError(f"Table '{table_name}' in schema '{schema_name}' has no primary key defined or detectable.")

    stmt = table.delete().where(pk_column == primary_key_value)
    try:
        result = db.execute(stmt)
        db.commit()
        if result.rowcount == 0:
            raise ValueError(f"No row found with primary key '{primary_key_value}' to delete.")
    except SQLAlchemyError as e:
        db.rollback()
        raise e