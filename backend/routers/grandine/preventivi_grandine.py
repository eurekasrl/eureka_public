from uuid import UUID
import traceback
from typing import Tuple

from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session


from db.db import get_db
from schemas.grandine import PreventivoGrandine, PreventivoGrandineCreate, PreventivoGrandinePatch
from crud.grandine.preventivo import get_grandine_preventivo, create_grandine_preventivo_entry, patch_grandine_preventivo_entry

router = APIRouter()

@router.get("/{sale_preventivo_id}", response_model = PreventivoGrandine)
def read_preventivo_grandine(sale_preventivo_id: UUID, db: Session = Depends(get_db)) -> PreventivoGrandine:
    return get_grandine_preventivo(db, sale_preventivo_id)

@router.post("/", response_model=str, status_code=status.HTTP_201_CREATED)
def create_preventivo_grandine(preventivo_data: PreventivoGrandineCreate, db:Session = Depends(get_db))-> str:
    """
    Create a new Grandine Preventivo.
    Accepts payload defined in PreventivoGrandineCreate schema.
    """
    try:
        return create_grandine_preventivo_entry(db, preventivo_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il salvataggio del preventivo: {str(e)}"
        )

@router.patch("/", response_model=Tuple[bool, str], status_code=status.HTTP_202_ACCEPTED)
def patch_preventivo_grandine(preventivo_data: PreventivoGrandinePatch, db:Session = Depends(get_db))-> Tuple[bool, str]:
    existing_preventivo_grandine_db = get_grandine_preventivo(db, preventivo_data.sale_preventivo_id)

    if not existing_preventivo_grandine_db:
        raise HTTPException(status_code=404, detail="Preventivo Grandine not found")
    
    return patch_grandine_preventivo_entry(db, existing_preventivo_grandine_db, preventivo_data)
    