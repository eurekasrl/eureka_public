from typing import List, Dict, Any, Optional
from datetime import date, datetime
import uuid
import json

from fastapi import Depends, HTTPException, status, APIRouter, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import RootModel

from db.db import get_db
from crud import dynamic_table as dynamic_crud
from crud.grandine.preventivo import reset_preventivo_grandine_by_pu

router = APIRouter()


@router.get("/", response_model=List[Dict[str, str]], summary="Get all table names in the database")
def get_tables():
    """
    Returns a list of all table names available in the configured database,
    including their respective schemas.
    """
    return dynamic_crud.get_all_table_names()

@router.get("/{schema_name}/{table_name}/schema/", response_model=List[Dict[str, Any]], summary="Get table schema (columns and types)")
def get_table_structure(schema_name: str, table_name: str):
    """
    Returns the column names, types, and other metadata for a specified table.
    """
    try:
        return dynamic_crud.get_table_schema(table_name, schema_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Table or schema not found: {e}")

@router.get("/{schema_name}/{table_name}/data/", response_model=List[Dict[str, Any]], summary="Get data from a specific table")
def get_table_data(
    schema_name: str, 
    table_name: str,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[str] = Query(None, description="JSON string of filters, e.g., '{\"column_name\": \"value\"}'")
    ):
    """
    Retrieves data rows from a specified table.
    Supports pagination with `skip` and `limit` parameters.
    Supports filtering with a JSON string in the `filters` query parameter.
    """
    parsed_filters = {}
    if filters:
        try:
            parsed_filters = json.loads(filters)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format for filters parameter.")
    try:
        data = dynamic_crud.get_table_data(table_name, schema_name, skip, limit, parsed_filters)
        # Convert date/datetime objects to string for JSON serialization if necessary
        # Pydantic (implicitly used by FastAPI) usually handles this well, but explicit conversion can be done if issues arise.
        for row in data:
            for key, value in row.items():
                if isinstance(value, (datetime, date)):
                    row[key] = value.isoformat()
        return data
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

# Pydantic model for dynamic row data (used for POST/PUT)
class DynamicRowData(RootModel[Dict[str, Any]]):
    pass # Allow any dictionary as input

@router.post("/{schema_name}/{table_name}/data/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED, summary="Add a new row to a table")
def add_row_to_table(schema_name: str, table_name: str, row_data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Adds a new row to the specified table.
    The request body should be a JSON object where keys are column names and values are the data for the new row.
    """
    try:
        if ('id' not in row_data or not row_data['id']) and table_name!='persona_fisica':
            row_data['id'] = str(uuid.uuid4()) # Generate UUID in Python if not provided
            
        new_row = dynamic_crud.add_table_row(db, table_name, schema_name, row_data)
        return new_row
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e.args[0]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding row: {e}")

@router.put("/{schema_name}/{table_name}/data/{primary_key_value}", response_model=Dict[str, Any], summary="Update an existing row in a table")
def update_row_in_table(
    schema_name: str,
    table_name: str,
    primary_key_value: str, # Primary key values are often strings (for UUIDs) or integers
    row_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Updates an existing row in the specified table, identified by its primary key.
    The request body should be a JSON object where keys are column names and values are the updated data.
    """
    try:
        updated_row = dynamic_crud.update_table_row(db, table_name, schema_name, primary_key_value, row_data)
        if schema_name == 'grandine' and table_name=='piano_utilizzo':
            reset_preventivo_grandine_by_pu(db = db, piano_utilizzo_id= primary_key_value)
        elif schema_name == 'grandine' and table_name=='piano_utilizzo_dettagliato':
            reset_preventivo_grandine_by_pu(db = db, piano_utilizzo_dettagliato_id= primary_key_value)
        return updated_row
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e.args[0]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating row: {e}")

@router.delete("/{schema_name}/{table_name}/data/{primary_key_value}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a row from a table")
def delete_row_from_table(schema_name: str, table_name: str, primary_key_value: str, db: Session = Depends(get_db)):
    """
    Deletes a row from the specified table, identified by its primary key.
    """
    try:
        dynamic_crud.delete_table_row(db, table_name, schema_name, primary_key_value)
        return {} # No content
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e.args[0]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting row: {e}")
