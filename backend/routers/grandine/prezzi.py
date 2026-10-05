from typing import List, Optional

from fastapi import Depends, HTTPException, APIRouter, Query
from sqlalchemy.orm import Session


from db.db import get_db
from schemas.grandine import Prezzi
from crud.grandine.prezzi import get_prezzi_for_area
from crud.core.condifesa import get_condifesa_by_id

router = APIRouter()

@router.get("/list", response_model = List[Prezzi])
def read_prezzi(
        db: Session = Depends(get_db),
        anno: Optional[int] = Query(None, description="Optional search for anno"),
        condifesa_id: Optional[str] = Query(None, description="Optional search for condifesa_id"),
        prodotto_id: Optional[str] = Query(None, description="Optional search for prodotto_id")
):
    condifesa_db = get_condifesa_by_id(db, condifesa_id)
    individuale = True if condifesa_db.nome=='INDIVIDUALE' else False

    return get_prezzi_for_area (db, anno, condifesa_id, prodotto_id, individuale)