from typing import List
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from db.db import get_db
from schemas.core import Compagnia
from crud.core.compagnie import get_compagnie

router = APIRouter()

@router.get("/list", response_model=List[Compagnia])
def read_compagnie(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_compagnie (db, skip=skip, limit=limit)