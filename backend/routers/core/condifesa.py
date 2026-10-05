from typing import List
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from db.db import get_db
from schemas.core import Condifesa
from crud.core.condifesa import get_condifesa, get_condifesa_by_id


router = APIRouter()

@router.get("/list", response_model=List[Condifesa])
def read_condifesa(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_condifesa (db, skip=skip, limit=limit)

@router.get("/{condifesa_id}", response_model=Condifesa)
def read_condifesa_by_id(condifesa_id: str, db: Session = Depends(get_db)):
    return get_condifesa_by_id(db, condifesa_id=condifesa_id)